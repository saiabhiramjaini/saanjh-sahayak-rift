"""fix_code node — asks the LLM to repair a failing file and applies it via the EC2 agent."""

import asyncio
import logging

from src.state.graph_state import GraphState
from src.llm.llm_client import ask_llm
from src.services.ec2_client import EC2Client

logger = logging.getLogger("rift_server")


def fix_code(state: GraphState) -> GraphState:
    """Generate a fix with the LLM and apply it to the EC2 session."""

    if state["passed"]:
        return state

    error = state["current_error"]
    file_path = error.get("file", "unknown")

    prompt = f"""CI pipeline failed.

File: {file_path}
Error Type: {error.get('error_type')}
Message: {error.get('message')}
Full Trace:
{error.get('full_trace', '(none)')}

Fix the issue with a minimal change. Return only the complete corrected file contents."""

    logger.info(f"fix_code: asking LLM to fix {file_path}")
    fixed_code = ask_llm(prompt)

    async def _apply() -> dict:
        client = EC2Client()
        return await client.apply_fix(
            session_id=state["session_id"],
            file_path=file_path,
            fix_content=fixed_code,
            install_command=state.get("install_command"),
            test_command=state.get("test_command"),
        )

    result = asyncio.run(_apply())
    logger.info(f"fix_code: apply_fix success={result.get('success')}")

    fixed_files: list[str] = state.get("fixed_files", [])
    if file_path not in fixed_files:
        fixed_files.append(file_path)
    state["fixed_files"] = fixed_files

    return state
