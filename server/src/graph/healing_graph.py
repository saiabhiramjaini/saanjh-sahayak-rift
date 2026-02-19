from langgraph.graph import StateGraph, END
from state.graph_state import GraphState

from nodes.execute_tests import execute_tests
from nodes.select_error import select_error
from nodes.fix_code import fix_code

def build_graph():

    builder = StateGraph(GraphState)

    builder.add_node("execute_tests", execute_tests)
    builder.add_node("select_error", select_error)
    builder.add_node("fix_code", fix_code)

    builder.set_entry_point("execute_tests")

    builder.add_edge("execute_tests", "select_error")

    def decide(state: GraphState):
        if state["passed"]:
            return "end"
        return "fix"

    builder.add_conditional_edges(
        "select_error",
        decide,
        {
            "fix": "fix_code",
            "end": END,
        },
    )

    builder.add_edge("fix_code", "execute_tests")

    return builder.compile()
