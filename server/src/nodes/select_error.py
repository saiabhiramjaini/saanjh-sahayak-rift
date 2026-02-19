from state.graph_state import GraphState

def select_error(state: GraphState) -> GraphState:

    if state["passed"] or not state["errors"]:
        return state

    state["current_error"] = state["errors"][0]
    return state
