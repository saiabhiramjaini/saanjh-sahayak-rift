from state.graph_state import GraphState
from llm.llm_client import ask_llm
from tools.file_tools import read_file, write_file

def fix_code(state: GraphState) -> GraphState:

    if state["passed"]:
        return state

    error = state["current_error"]
    file_path = error["file"]

    code = read_file(state["session_id"], file_path)

    prompt = f"""
You are an expert Python software engineer.

A CI pipeline failed.

File: {file_path}
Error Type: {error.get('error_type')}
Message: {error.get('message')}

Code:
{code}

Fix the issue with minimal change.
Return only corrected code.
"""

    fixed_code = ask_llm(prompt)

    write_file(state["session_id"], file_path, fixed_code)

    return state
