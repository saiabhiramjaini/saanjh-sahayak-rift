"""healing_graph — LangGraph pipeline that iteratively tests and fixes a repository."""

from langgraph.graph import StateGraph, END

from src.state.graph_state import GraphState
from src.nodes.execute_tests import execute_tests
from src.nodes.select_error import select_error
from src.nodes.fix_code import fix_code


def build_graph():
    """Build and compile the healing state graph."""

    builder: StateGraph = StateGraph(GraphState)

    builder.add_node("execute_tests", execute_tests)
    builder.add_node("select_error", select_error)
    builder.add_node("fix_code", fix_code)

    builder.set_entry_point("execute_tests")
    builder.add_edge("execute_tests", "select_error")

    def decide(state: GraphState) -> str:
        if state["passed"]:
            return "end"
        if state.get("iteration", 0) >= state.get("max_iterations", 5):
            return "end"
        return "fix"

    builder.add_conditional_edges(
        "select_error",
        decide,
        {"fix": "fix_code", "end": END},
    )

    builder.add_edge("fix_code", "execute_tests")

    return builder.compile()
