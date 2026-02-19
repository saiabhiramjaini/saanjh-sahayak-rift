from fastapi import APIRouter

from src.app.handlers import handle_endpoint
from src.models import ApplyFixRequest
from src.services.git_service import GitService
from src.services.session_store import session_store

router = APIRouter(tags=["Fix"])


@router.post("/fix")
@handle_endpoint
async def apply_fix(request: ApplyFixRequest):
    """Apply an AI-generated fix to the repo."""
    # Validate session exists (raises SessionNotFoundError if missing)
    session = session_store.get(request.session_id)

    git_service = GitService()

    # 1. Create/checkout the fix branch
    git_service.create_branch(request.session_id, request.branch_name)

    # 2. Write the fixed file
    git_service.write_file(request.session_id, request.file_path, request.fix_content)

    # 3. Commit and push with [AI-AGENT] prefix
    commit_hash = git_service.commit_and_push(
        session_id=request.session_id,
        file_path=request.file_path,
        message=request.commit_message,  # Should already have [AI-AGENT] prefix
        branch_name=request.branch_name,
    )

    # Update session status in Redis
    session_store.update(request.session_id, {"status": "fixed"})

    return {
        "success": True,
        "commit_hash": commit_hash,
        "message": f"Fix applied and pushed to {request.branch_name}",
    }