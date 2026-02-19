"""Agent run endpoint."""

from fastapi import APIRouter

from src.app.handlers import handle_endpoint
from src.models import AgentRunRequest, AgentRunResponse
from src.runner.agent_runner import run_agent

router = APIRouter(tags=["Agent"])


@router.post("/agent/run", response_model=AgentRunResponse, status_code=202)
@handle_endpoint
async def agent_run(request: AgentRunRequest) -> AgentRunResponse:
    """
    Clone a GitHub repo into an EC2 session, run the healing graph,
    and (optionally) commit fixes to a new branch.
    """
    result = await run_agent(
        repo_url=request.repo_url,
        language=request.language,
        user_id=request.user_id,
        install_command=request.install_command,
        test_command=request.test_command,
        branch=request.branch,
        max_iterations=request.max_iterations,
        auto_commit=request.auto_commit,
        commit_message=request.commit_message,
        branch_name=request.branch_name,
    )

    if result["passed"]:
        message = "All tests are passing."
        status = "passed"
    else:
        remaining = len(result["errors_remaining"])
        message = f"Max iterations reached. {remaining} error(s) remain."
        status = "partial_fix" if result["commit_hash"] else "failed"

    return AgentRunResponse(
        session_id=result["session_id"],
        status=status,
        passed=result["passed"],
        iterations=result["iterations"],
        errors_remaining=result["errors_remaining"],
        commit_hash=result.get("commit_hash"),
        branch_name=result.get("branch_name"),
        message=message,
    )
