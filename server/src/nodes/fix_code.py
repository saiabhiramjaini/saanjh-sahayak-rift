"""fix_code node — asks the LLM to repair a failing file and applies it via EC2 agent."""

import logging

from src.state.graph_state import GraphState
from src.llm.llm_client import ask_llm
from src.services.ec2_client import EC2Client

logger = logging.getLogger("rift_server")


async def fix_code(state: GraphState) -> GraphState:
    """Generate a fix with the LLM, apply it, and record in fixes_applied."""

    if state["passed"]:
        return state

    error = state["current_error"]
    file_path = error.get("file", "unknown")
    bug_type = error.get("error_type", "LOGIC")
    line_number = error.get("line")
    error_message = error.get("message", "")

    prompt = f"""CI pipeline failed.

File: {file_path}
Error Type: {bug_type}
Line: {line_number or 'unknown'}
Message: {error_message}
Full Trace:
{error.get('full_trace', '(none)')}

Fix the issue with a minimal change. Return only the complete corrected file contents."""

    logger.info(f"fix_code: asking LLM to fix {file_path} ({bug_type})")
    fixed_code = ask_llm(prompt)

    client = EC2Client()
    result = await client.apply_fix(
        session_id=state["session_id"],
        file_path=file_path,
        fix_content=fixed_code,
        install_command=state.get("install_command"),
        test_command=state.get("test_command"),
    )
    fix_success = result.get("success", False)
    logger.info(f"fix_code: apply_fix success={fix_success}")

    # Build commit message
    commit_msg = f"[AI-AGENT] Fix {bug_type} in {file_path}"
    if line_number:
        commit_msg += f" at line {line_number}"

    # Record in fixes_applied
    fixes: list = state.get("fixes_applied", [])
    fixes.append({
        "file": file_path,
        "bug_type": bug_type,
        "line_number": line_number,
        "commit_message": commit_msg,
        "status": "fixed" if fix_success else "failed",
    })
    state["fixes_applied"] = fixes

    # Track unique fixed files
    fixed_files: list[str] = state.get("fixed_files", [])
    if file_path not in fixed_files:
        fixed_files.append(file_path)
    state["fixed_files"] = fixed_files

    return state
