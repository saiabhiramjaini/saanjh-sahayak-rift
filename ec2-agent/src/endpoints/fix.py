from fastapi import APIRouter

from src.app.handlers import handle_endpoint
from src.models import ApplyFixRequest, CommitFixRequest
from src.services.git_service import GitService
from src.services.session_store import session_store
from src.services.test_runner import TestRunner

router = APIRouter(tags=["Fix"])


@router.post("/fix")
@handle_endpoint
async def apply_fix(request: ApplyFixRequest):
    """Apply AI-generated fix locally and run tests (no git operations)."""
    # Validate session exists (raises SessionNotFoundError if missing)
    session = session_store.get(request.session_id)

    git_service = GitService()

    # 1. Write the fixed file to disk
    git_service.write_file(request.session_id, request.file_path, request.fix_content)

    # 2. Run tests with the fix applied
    test_runner = TestRunner()
    result = test_runner.run_tests(
        repo_url=session["repo_url"],
        session_id=request.session_id,
        language=session["language"],
        branch="main",  # Not switching branches, just testing current state
        install_command=request.install_command,
        test_command=request.test_command,
    )

    # Update session status in Redis
    new_status = "fix_verified" if result.status == "success" else "fix_failed"
    session_store.update(request.session_id, {"status": new_status})

    return {
        "success": result.status == "success",
        "file_updated": True,
        "test_result": result.dict(),
        "message": f"Fix applied. Tests {'passed' if result.status == 'success' else 'failed'}.",
    }


@router.post("/commit")
@handle_endpoint
async def commit_fix(request: CommitFixRequest):
    """Create branch, commit changes, and push to GitHub."""
    # Validate session exists (raises SessionNotFoundError if missing)
    session = session_store.get(request.session_id)

    git_service = GitService()

    # 1. Create/checkout the fix branch
    git_service.create_branch(request.session_id, request.branch_name)

    # 2. Commit and push (file should already be written by /fix)
    commit_hash = git_service.commit_and_push(
        session_id=request.session_id,
        file_path=request.file_path,
        message=request.commit_message,
        branch_name=request.branch_name,
    )

    # Update session status in Redis
    session_store.update(request.session_id, {"status": "committed"})

    return {
        "success": True,
        "commit_hash": commit_hash,
        "branch_name": request.branch_name,
        "message": f"Changes committed and pushed to {request.branch_name}",
    }