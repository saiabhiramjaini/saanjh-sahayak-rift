"""Pull Request creation endpoint — uses GitHub API to create PRs."""

import logging
from typing import Optional

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger("rift_server")

router = APIRouter(tags=["Pull Request"])


class CreatePRRequest(BaseModel):
    """Request body for POST /pr — create a GitHub Pull Request."""

    repo_full_name: str = Field(..., description="Full repo name (owner/repo)")
    branch_name: str = Field(..., description="Head branch name with the fixes")
    base_branch: str = Field(default="main", description="Base branch to merge into")
    title: str = Field(..., description="PR title")
    body: str = Field(default="", description="PR description body")
    github_token: str = Field(..., description="GitHub OAuth access token")


class CreatePRResponse(BaseModel):
    """Response for PR creation."""

    success: bool
    pr_url: Optional[str] = None
    pr_number: Optional[int] = None
    message: str = ""


@router.post("/pr", response_model=CreatePRResponse)
async def create_pull_request(request: CreatePRRequest):
    """Create a Pull Request on GitHub.

    Uses the user's GitHub OAuth token (from NextAuth) to create a PR
    from the AI fix branch to the base branch.
    """
    github_api = "https://api.github.com"
    url = f"{github_api}/repos/{request.repo_full_name}/pulls"

    headers = {
        "Authorization": f"Bearer {request.github_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    payload = {
        "title": request.title,
        "body": request.body,
        "head": request.branch_name,
        "base": request.base_branch,
    }

    logger.info(f"[PR] Creating PR: {request.repo_full_name} {request.branch_name} → {request.base_branch}")

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers=headers)

            if response.status_code == 201:
                data = response.json()
                pr_url = data.get("html_url", "")
                pr_number = data.get("number")
                logger.info(f"[PR] Created successfully: {pr_url}")
                return CreatePRResponse(
                    success=True,
                    pr_url=pr_url,
                    pr_number=pr_number,
                    message=f"Pull request #{pr_number} created successfully",
                )

            elif response.status_code == 422:
                # Often means PR already exists or no diff
                data = response.json()
                errors = data.get("errors", [])
                message = data.get("message", "")
                if errors:
                    message = errors[0].get("message", message)
                logger.warning(f"[PR] GitHub 422: {message}")
                return CreatePRResponse(
                    success=False,
                    message=f"Cannot create PR: {message}",
                )

            else:
                detail = response.text[:500]
                logger.error(f"[PR] GitHub API error {response.status_code}: {detail}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"GitHub API error: {detail}",
                )

    except httpx.ConnectError as e:
        logger.error(f"[PR] Cannot reach GitHub API: {e}")
        raise HTTPException(status_code=502, detail=f"Cannot reach GitHub API: {e}")
