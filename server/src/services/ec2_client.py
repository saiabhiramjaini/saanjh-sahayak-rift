"""HTTP client for talking to the EC2 agent service."""

import logging

import httpx

from src.app.config import api_settings
from src.core.exceptions import EC2AgentError, EC2AgentUnreachable

logger = logging.getLogger("rift_server")


class EC2Client:
    """
    Async HTTP client wrapping all ec2-agent API calls.

    All methods raise EC2AgentError on non-2xx responses,
    or EC2AgentUnreachable if the agent cannot be reached.
    """

    def __init__(self):
        self.base_url = api_settings.ec2_agent_url.rstrip("/")
        self.headers = {}
        if api_settings.ec2_agent_api_key:
            self.headers["X-API-Key"] = api_settings.ec2_agent_api_key

    def _client(self) -> httpx.AsyncClient:
        """Create an async HTTP client with shared config."""
        return httpx.AsyncClient(
            base_url=self.base_url,
            headers=self.headers,
            timeout=300.0,  # Long timeout — Docker test runs can take time
        )

    async def ping(self) -> bool:
        """Check ec2-agent health. Raises EC2AgentUnreachable on failure."""
        try:
            async with self._client() as client:
                response = await client.get("/api/v1/health")
                response.raise_for_status()
                logger.info(f"EC2 agent health: {response.json()}")
                return True
        except httpx.ConnectError as e:
            raise EC2AgentUnreachable(
                f"Cannot reach EC2 agent at {self.base_url}: {e}"
            )

    async def create_session(
        self,
        repo_url: str,
        language: str,
        user_id: str | None = None,
    ) -> dict:
        """POST /api/v1/sessions — clone repo and create a session."""
        try:
            async with self._client() as client:
                params = {"repo_url": repo_url, "language": language}
                if user_id:
                    params["user_id"] = user_id
                response = await client.post("/api/v1/sessions", params=params)
                self._raise_for_status(response, "create_session")
                return response.json()
        except (EC2AgentError, EC2AgentUnreachable):
            raise
        except httpx.ConnectError as e:
            raise EC2AgentUnreachable(str(e))

    async def execute_tests(
        self,
        session_id: str,
        install_command: str | None = None,
        test_command: str | None = None,
        branch: str = "main",
    ) -> dict:
        """POST /api/v1/execute — run tests for a session."""
        payload = {"session_id": session_id, "branch": branch}
        if install_command:
            payload["install_command"] = install_command
        if test_command:
            payload["test_command"] = test_command

        try:
            async with self._client() as client:
                response = await client.post("/api/v1/execute", json=payload)
                self._raise_for_status(response, "execute_tests")
                return response.json()
        except (EC2AgentError, EC2AgentUnreachable):
            raise
        except httpx.ConnectError as e:
            raise EC2AgentUnreachable(str(e))

    async def apply_fix(
        self,
        session_id: str,
        file_path: str,
        fix_content: str,
        install_command: str | None = None,
        test_command: str | None = None,
    ) -> dict:
        """POST /api/v1/fix — write fixed file and run tests."""
        payload = {
            "session_id": session_id,
            "file_path": file_path,
            "fix_content": fix_content,
        }
        if install_command:
            payload["install_command"] = install_command
        if test_command:
            payload["test_command"] = test_command

        try:
            async with self._client() as client:
                response = await client.post("/api/v1/fix", json=payload)
                self._raise_for_status(response, "apply_fix")
                return response.json()
        except (EC2AgentError, EC2AgentUnreachable):
            raise
        except httpx.ConnectError as e:
            raise EC2AgentUnreachable(str(e))

    async def commit_fix(
        self,
        session_id: str,
        file_path: str,
        commit_message: str,
        branch_name: str = "AI_Fix",
    ) -> dict:
        """POST /api/v1/commit — create branch, commit, push."""
        payload = {
            "session_id": session_id,
            "file_path": file_path,
            "commit_message": commit_message,
            "branch_name": branch_name,
        }
        try:
            async with self._client() as client:
                response = await client.post("/api/v1/commit", json=payload)
                self._raise_for_status(response, "commit_fix")
                return response.json()
        except (EC2AgentError, EC2AgentUnreachable):
            raise
        except httpx.ConnectError as e:
            raise EC2AgentUnreachable(str(e))

    async def delete_session(self, session_id: str) -> dict:
        """DELETE /api/v1/sessions/{session_id} — clean up session."""
        try:
            async with self._client() as client:
                response = await client.delete(f"/api/v1/sessions/{session_id}")
                self._raise_for_status(response, "delete_session")
                return response.json()
        except (EC2AgentError, EC2AgentUnreachable):
            raise
        except httpx.ConnectError as e:
            raise EC2AgentUnreachable(str(e))

    async def get_session(self, session_id: str) -> dict:
        """GET /api/v1/sessions/{session_id}."""
        try:
            async with self._client() as client:
                response = await client.get(f"/api/v1/sessions/{session_id}")
                self._raise_for_status(response, "get_session")
                return response.json()
        except (EC2AgentError, EC2AgentUnreachable):
            raise
        except httpx.ConnectError as e:
            raise EC2AgentUnreachable(str(e))

    # ── Internal ──────────────────────────────────────────

    def _raise_for_status(self, response: httpx.Response, operation: str) -> None:
        """Raise EC2AgentError for non-2xx responses with context."""
        if response.is_success:
            return
        try:
            detail = response.json().get("detail", response.text)
        except Exception:
            detail = response.text
        raise EC2AgentError(
            f"EC2 agent [{operation}] {response.status_code}: {detail}"
        )
