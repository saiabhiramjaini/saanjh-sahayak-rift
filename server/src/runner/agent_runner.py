import uuid
from graph.healing_graph import build_graph

def start_agent(repo_url: str):

    graph = build_graph()

    session_id = str(uuid.uuid4())

    state = {
        "repo_url": repo_url,
        "session_id": session_id,
        "branch": "main",
        "errors": [],
        "passed": False,
        "current_error": None,
        "iteration": 0,
        "max_iterations": 5,
    }

    return graph.invoke(state)
