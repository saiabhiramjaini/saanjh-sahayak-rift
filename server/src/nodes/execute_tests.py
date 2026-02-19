"""execute_tests node — calls the EC2 agent over HTTP to run the test suite."""

import logging
from datetime import datetime, timezone

from src.state.graph_state import GraphState
from src.services.ec2_client import EC2Client

logger = logging.getLogger("rift_server")


async def execute_tests(state: GraphState) -> GraphState:
    """Run tests via the EC2 agent, update state, and record CI timeline entry."""

    client = EC2Client()
    result = await client.execute_tests(
        session_id=state["session_id"],
        install_command=state.get("install_command"),
        test_command=state.get("test_command"),
        branch=state.get("branch", "main"),
    )

    errors = result.get("errors", [])
    passed = result.get("status") == "success"
    iteration = state.get("iteration", 0) + 1

    state["errors"] = errors
    state["passed"] = passed
    state["iteration"] = iteration

    # Track total unique failures detected (on first run)
    if iteration == 1:
        state["total_failures_detected"] = len(errors)
    elif len(errors) > state.get("total_failures_detected", 0):
        state["total_failures_detected"] = len(errors)

    # Record CI timeline entry
    fixes_so_far = len(state.get("fixes_applied", []))
    timeline: list = state.get("ci_timeline", [])
    timeline.append({
        "iteration": iteration,
        "status": "passed" if passed else "failed",
        "errors_count": len(errors),
        "fixes_applied": fixes_so_far,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
    state["ci_timeline"] = timeline

    logger.info(
        f"execute_tests iter={iteration} passed={passed} errors={len(errors)}"
    )
    return state
