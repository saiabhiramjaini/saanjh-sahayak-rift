"""execute_tests node — calls the EC2 agent over HTTP to run the test suite."""

import asyncio
import logging

from src.state.graph_state import GraphState
from src.services.ec2_client import EC2Client

logger = logging.getLogger("rift_server")


def execute_tests(state: GraphState) -> GraphState:
    """Run tests via the EC2 agent and update state with results."""

    async def _run() -> dict:
        client = EC2Client()
        return await client.execute_tests(
            session_id=state["session_id"],
            install_command=state.get("install_command"),
            test_command=state.get("test_command"),
            branch=state.get("branch", "main"),
        )

    result = asyncio.run(_run())

    state["errors"] = result.get("errors", [])
    state["passed"] = result.get("status") == "success"
    state["iteration"] = state.get("iteration", 0) + 1

    logger.info(
        f"execute_tests iter={state['iteration']} "
        f"passed={state['passed']} errors={len(state['errors'])}"
    )
    return state
