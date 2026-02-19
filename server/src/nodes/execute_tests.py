from state.graph_state import GraphState
from tools.ci_tools import run_ci

def execute_tests(state: GraphState) -> GraphState:

    response = run_ci(
        repo_url=state["repo_url"],
        session_id=state["session_id"],
    )

    state["errors"] = response.errors
    state["passed"] = response.status == "success"

    return state
