"""select_error node — picks the first unresolved error to fix next."""

from src.state.graph_state import GraphState


async def select_error(state: GraphState) -> GraphState:
    """Set current_error to the first error in the list."""

    if state["passed"] or not state["errors"]:
        return state

    state["current_error"] = state["errors"][0]
    return state
