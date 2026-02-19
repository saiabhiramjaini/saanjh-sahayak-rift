"""agent_runner — creates an EC2 session, runs the healing graph, optionally commits."""

import logging
from typing import Any

from src.app.config import api_settings
from src.graph.healing_graph import build_graph
from src.services.ec2_client import EC2Client

logger = logging.getLogger("rift_server")


async def run_agent(
    repo_url: str,
    language: str,
    user_id: str | None = None,
    install_command: str | None = None,
    test_command: str | None = None,
    branch: str = "main",
    max_iterations: int | None = None,
    auto_commit: bool = False,
    commit_message: str = "[AI-AGENT] Fix CI failures",
    branch_name: str = "AI_Fix",
) -> dict[str, Any]:
    """
    End-to-end agent run:
    1. Create EC2 session (clone repo).
    2. Run healing graph (test → select → fix loop).
    3. If auto_commit=True and files were fixed, commit each file.
    4. Return summary dict.
    """
    client = EC2Client()

    logger.info(f"run_agent: creating session for {repo_url}")
    session = await client.create_session(repo_url, language, user_id)
    session_id: str = session["session_id"]
    logger.info(f"run_agent: session={session_id}")

    graph = build_graph()

    initial_state: dict[str, Any] = {
        "session_id": session_id,
        "repo_url": repo_url,
        "language": language,
        "branch": branch,
        "install_command": install_command,
        "test_command": test_command,
        "errors": [],
        "passed": False,
        "current_error": None,
        "iteration": 0,
        "max_iterations": max_iterations or api_settings.max_iterations,
        "auto_commit": auto_commit,
        "commit_message": commit_message,
        "branch_name": branch_name,
        "fixed_files": [],
        "commit_hash": None,
    }

    final_state: dict[str, Any] = graph.invoke(initial_state)
    logger.info(
        f"run_agent: graph finished passed={final_state['passed']} "
        f"iters={final_state['iteration']} fixed={final_state['fixed_files']}"
    )

    commit_hash: str | None = None

    if auto_commit and final_state["fixed_files"]:
        for file_path in final_state["fixed_files"]:
            logger.info(f"run_agent: committing {file_path}")
            result = await client.commit_fix(
                session_id=session_id,
                file_path=file_path,
                commit_message=commit_message,
                branch_name=branch_name,
            )
            if result.get("success"):
                commit_hash = result.get("commit_hash")

    return {
        "session_id": session_id,
        "passed": final_state["passed"],
        "iterations": final_state["iteration"],
        "errors_remaining": final_state["errors"],
        "commit_hash": commit_hash,
        "branch_name": branch_name if commit_hash else None,
    }
