"""GraphState — shared state flowing through the LangGraph healing pipeline."""

from typing import TypedDict, Any


class GraphState(TypedDict):
    """State schema for the healing graph."""

    # ── Session ──
    session_id: str          # EC2 agent session ID
    repo_url: str            # GitHub repository URL
    language: str            # python or nodejs
    branch: str              # Git branch (e.g. "main")

    # ── Test execution ──
    install_command: str | None   # Optional custom install command
    test_command: str | None      # Optional custom test command
    errors: list[dict[str, Any]]  # Test errors from last run
    passed: bool                  # Whether all tests pass

    # ── Iteration control ──
    current_error: dict[str, Any] | None  # Error currently being fixed
    iteration: int                         # Current iteration (0-indexed)
    max_iterations: int                    # Stop after this many iterations

    # ── Commit ──
    auto_commit: bool           # Whether to commit fixes after completion
    commit_message: str         # Commit message
    branch_name: str            # Branch name for the fix
    fixed_files: list[str]      # Files modified during this run
    commit_hash: str | None     # Set after successful commit
