"""Pydantic models for the agent endpoint."""

from pydantic import BaseModel, Field


class AgentRunRequest(BaseModel):
    """Request body for POST /agent/run."""

    repo_url: str = Field(..., description="GitHub repository URL")
    language: str = Field(..., description="Project language: python or nodejs")
    user_id: str | None = Field(default=None, description="Optional user identifier")
    install_command: str | None = Field(
        default=None, description="Custom dependency install command"
    )
    test_command: str | None = Field(
        default=None, description="Custom test execution command"
    )
    branch: str = Field(default="main", description="Branch to clone and test")
    max_iterations: int | None = Field(
        default=None,
        description="Override max healing iterations (default from config)",
    )
    auto_commit: bool = Field(
        default=False,
        description="Auto-commit and push after all fixes are applied",
    )
    commit_message: str = Field(
        default="[AI-AGENT] Automated fix by RIFT agent",
        description="Commit message prefix",
    )
    branch_name: str = Field(
        default="AI_Fix",
        description="Branch name for pushing fixes",
    )


class AgentRunResponse(BaseModel):
    """Response body from POST /agent/run."""

    session_id: str = Field(..., description="EC2 agent session ID")
    status: str = Field(..., description="final | running | failed")
    passed: bool = Field(..., description="Whether tests pass after all iterations")
    iterations: int = Field(..., description="Number of healing iterations performed")
    errors_remaining: list[dict] = Field(
        default=[],
        description="Remaining test errors (empty if passed)",
    )
    commit_hash: str | None = Field(
        default=None, description="Commit hash if auto_commit was True"
    )
    branch_name: str | None = Field(
        default=None, description="Branch name if auto_commit was True"
    )
    message: str = Field(default="", description="Human-readable status message")
