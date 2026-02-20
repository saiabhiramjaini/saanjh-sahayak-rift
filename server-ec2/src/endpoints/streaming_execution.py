"""Streaming execution endpoint — real-time test output via SSE."""

import json
import logging
import os
import time
from typing import Generator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from src.app.handlers import handle_endpoint
from src.models import ExecuteTestsRequest
from src.services.docker_service import DockerService
from src.services.git_service import GitService
from src.services.session_store import session_store
from src.utils.parsers import parse_test_output

logger = logging.getLogger("ec2_agent")

router = APIRouter(tags=["Streaming Execution"])


def _sse_event(data: dict) -> str:
    """Format a dict as an SSE event line."""
    return f"data: {json.dumps(data)}\n\n"


def _stream_execution(
    session: dict,
    session_id: str,
    language: str,
    branch: str,
    install_command: str | None,
    test_command: str | None,
) -> Generator[str, None, None]:
    """Generator that streams test execution output as SSE events."""

    docker_service = DockerService()
    git_service = GitService()

    repo_path = git_service.get_repo_path(session_id)
    if not os.path.exists(repo_path):
        repo_path = git_service.clone_repo(
            repo_url=session["repo_url"],
            session_id=session_id,
            branch=branch,
        )

    from src.app.config import api_settings
    container_repo_path = os.path.join(api_settings.container_repos_path, session_id)

    # ── Install ──────────────────────────────────────────────────────────
    yield _sse_event({"type": "phase", "phase": "install"})

    install_lines: list[str] = []
    install_exit = 0
    try:
        gen = docker_service.install_dependencies_streaming(
            language=language,
            repo_path=container_repo_path,
            custom_command=install_command,
        )
        for line in gen:
            install_lines.append(line)
            yield _sse_event({"type": "log", "phase": "install", "line": line})
    except Exception as e:
        logger.warning(f"Install streaming failed, falling back: {e}")
        install_exit, install_output = docker_service.install_dependencies(
            language=language,
            repo_path=container_repo_path,
            custom_command=install_command,
        )
        for line in install_output.strip().split("\n"):
            install_lines.append(line)
            yield _sse_event({"type": "log", "phase": "install", "line": line})

    yield _sse_event({"type": "phase_done", "phase": "install", "exit_code": install_exit})

    # ── Test ─────────────────────────────────────────────────────────────
    yield _sse_event({"type": "phase", "phase": "test"})

    test_lines: list[str] = []
    test_exit = 0
    full_test_output = ""
    try:
        gen = docker_service.run_tests_streaming(
            language=language,
            repo_path=container_repo_path,
            custom_command=test_command,
        )
        # Manually drive the generator so we can capture its return value
        # (exit_code, full_output) which is set via `return` inside the generator.
        try:
            while True:
                line = next(gen)
                test_lines.append(line)
                yield _sse_event({"type": "log", "phase": "test", "line": line})
        except StopIteration as stop:
            if stop.value:
                test_exit, full_test_output = stop.value
            else:
                test_exit = 0
                full_test_output = "\n".join(test_lines)
    except Exception as e:
        logger.warning(f"Test streaming failed, falling back: {e}")
        test_exit, full_test_output = docker_service.run_tests(
            language=language,
            repo_path=container_repo_path,
            custom_command=test_command,
        )
        for line in full_test_output.strip().split("\n"):
            test_lines.append(line)
            yield _sse_event({"type": "log", "phase": "test", "line": line})

    # Parse errors
    errors = parse_test_output(full_test_output, language)
    status = "success" if test_exit == 0 else "failed"

    # Count passed
    passed = _count_passed(full_test_output, language)
    failed = len(errors)
    duration = 0  # Will be measured by caller

    # ── Final result ──
    result = {
        "session_id": session_id,
        "status": status,
        "language": language,
        "passed": passed,
        "failed": failed,
        "errors": [{"file": e.file, "line": e.line, "message": e.message, "error_type": e.error_type, "full_trace": e.full_trace} for e in errors],
        "raw_output": full_test_output,
        "duration": duration,
    }

    yield _sse_event({"type": "result", "data": result})
    yield _sse_event({"type": "done"})


def _count_passed(output: str, language: str) -> int:
    """Extract number of passed tests from raw output."""
    if language == "python":
        for line in output.splitlines():
            if "passed" in line:
                for part in line.split():
                    if part.isdigit():
                        return int(part)
    elif language == "nodejs":
        for line in output.splitlines():
            if "passed" in line.lower():
                parts = line.split()
                for i, part in enumerate(parts):
                    if "passed" in part.lower() and i > 0:
                        num = parts[i - 1].replace(",", "")
                        if num.isdigit():
                            return int(num)
    return 0


@router.post("/execute/stream")
async def execute_tests_streaming(request: ExecuteTestsRequest):
    """Run tests with real-time SSE streaming output.

    Returns a text/event-stream response where each event is a JSON line:
    - {"type": "phase", "phase": "install"|"test"}
    - {"type": "log", "phase": "...", "line": "..."}
    - {"type": "phase_done", "phase": "...", "exit_code": N}
    - {"type": "result", "data": {...}}
    - {"type": "done"}
    """
    session = session_store.get(request.session_id)
    session_store.update(request.session_id, {"status": "running"})

    language = session["language"]
    branch = request.branch or "main"

    def generate():
        yield from _stream_execution(
            session=session,
            session_id=request.session_id,
            language=language,
            branch=branch,
            install_command=request.install_command,
            test_command=request.test_command,
        )

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
