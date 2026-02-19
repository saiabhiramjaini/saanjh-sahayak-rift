"""Session endpoints — Redis-backed CRUD + DELETE with repo cleanup."""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter

from src.app.handlers import handle_endpoint
from src.services.git_service import GitService
from src.services.session_store import session_store

router = APIRouter(tags=["Session"])


@router.post("/sessions", status_code=201)
@handle_endpoint
async def create_session(repo_url: str, language: str, user_id: str | None = None):
    """Clone repo and create a new session.

    Args:
        repo_url: GitHub repository URL
        language: Project language (python or nodejs)
        user_id: Optional user identifier (email, username, etc.)
    """
    session_id = str(uuid.uuid4())

    git_service = GitService()
    repo_path = git_service.clone_repo(repo_url, session_id)

    session_data = {
        "session_id": session_id,
        "user_id": user_id or "anonymous",
        "status": "cloned",
        "repo_url": repo_url,
        "language": language,
        "repo_path": str(repo_path),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    session_store.create(session_id, session_data)
    return session_data


@router.get("/sessions/{session_id}")
@handle_endpoint
async def get_session(session_id: str):
    """Get session details."""
    return session_store.get(session_id)


@router.get("/sessions")
@handle_endpoint
async def list_sessions(user_id: str | None = None):
    """List all sessions, optionally filtered by user_id.

    Args:
        user_id: Optional - filter sessions by user

    Returns:
        List of sessions with count
    """
    if user_id:
        sessions = session_store.list_by_user(user_id)
    else:
        sessions = session_store.list_all()

    return {"sessions": sessions, "count": len(sessions)}


@router.delete("/sessions/{session_id}")
@handle_endpoint
async def delete_session(session_id: str):
    """Delete a session and clean up its cloned repository.

    This performs two operations:
    1. Removes the session from Redis
    2. Deletes the cloned repo directory from disk
    """
    # Get session first (raises SessionNotFoundError if missing)
    session_data = session_store.get(session_id)

    # Clean up cloned repo from filesystem
    git_service = GitService()
    git_service.cleanup_session(session_id)

    # Delete from Redis (session + indexes)
    session_store.delete(session_id)

    return {
        "message": f"Session {session_id} deleted",
        "repo_cleaned": True,
        "repo_url": session_data.get("repo_url"),
    }