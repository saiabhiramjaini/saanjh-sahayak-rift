from typing import TypedDict, Any


class GraphState(TypedDict):
    """State schema for the healing graph."""
    
    repo_url: str
    session_id: str
    branch: str
    errors: list[dict[str, Any]]
    passed: bool
    current_error: dict[str, Any] | None
    iteration: int
    max_iterations: int
