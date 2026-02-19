"""agent_runner — full orchestration: session → graph → commit → score → results.json."""

import json
import logging
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.app.config import api_settings
from src.graph.healing_graph import build_graph
from src.services.ec2_client import EC2Client

logger = logging.getLogger("rift_server")


def _make_branch_name(team_name: str, leader_name: str) -> str:
    """
    Build branch name per hackathon rules:
    All UPPERCASE, spaces → underscores, ends with _AI_Fix.
    e.g. "RIFT ORGANISERS" + "Saiyam Kumar" → "RIFT_ORGANISERS_SAIYAM_KUMAR_AI_Fix"
    """
    clean = lambda s: re.sub(r"[^A-Z0-9_]", "", s.upper().replace(" ", "_"))
    return f"{clean(team_name)}_{clean(leader_name)}_AI_Fix"


def _calculate_score(
    total_commits: int,
    time_taken_seconds: float,
) -> dict[str, Any]:
    """Score per hackathon rules: base 100, +10 if <5min, -2 per commit over 20."""
    base = 100
    speed_bonus = 10 if time_taken_seconds < 300 else 0
    excess_commits = max(0, total_commits - 20)
    efficiency_penalty = excess_commits * 2
    final = max(0, base + speed_bonus - efficiency_penalty)
    return {
        "base_score": base,
        "speed_bonus": speed_bonus,
        "efficiency_penalty": efficiency_penalty,
        "total_commits": total_commits,
        "final_score": final,
    }


async def run_agent(
    repo_url: str,
    language: str,
    team_name: str,
    team_leader_name: str,
    install_command: str | None = None,
    test_command: str | None = None,
    branch: str = "main",
    max_iterations: int | None = None,
) -> dict[str, Any]:
    """
    End-to-end agent run:
    1. Create EC2 session (clone repo).
    2. Run LangGraph healing loop (test → select → fix → repeat).
    3. Commit each fixed file to branch TEAM_NAME_LEADER_AI_Fix.
    4. Calculate score, build results.json.
    5. Return everything the dashboard needs.
    """
    start_time = time.time()
    client = EC2Client()

    # ── 1. Branch name ──
    branch_name = _make_branch_name(team_name, team_leader_name)
    logger.info(f"run_agent: branch_name={branch_name}")

    # ── 2. Create session (clone repo) ──
    logger.info(f"run_agent: creating session for {repo_url}")
    session = await client.create_session(repo_url, language)
    session_id: str = session["session_id"]
    logger.info(f"run_agent: session={session_id}")

    # ── 3. Build & run the healing graph ──
    graph = build_graph()

    initial_state: dict[str, Any] = {
        "session_id": session_id,
        "repo_url": repo_url,
        "language": language,
        "branch": branch,
        "team_name": team_name,
        "team_leader_name": team_leader_name,
        "branch_name": branch_name,
        "install_command": install_command,
        "test_command": test_command,
        "errors": [],
        "passed": False,
        "current_error": None,
        "iteration": 0,
        "max_iterations": max_iterations or api_settings.max_iterations,
        "fixes_applied": [],
        "ci_timeline": [],
        "total_failures_detected": 0,
        "fixed_files": [],
        "commit_hash": None,
    }

    final_state: dict[str, Any] = await graph.ainvoke(initial_state)
    logger.info(
        f"run_agent: graph done passed={final_state['passed']} "
        f"iters={final_state['iteration']} fixes={len(final_state['fixes_applied'])}"
    )

    # ── 4. Commit all fixed files ──
    commit_hash: str | None = None
    total_commits = 0

    if final_state["fixed_files"]:
        for fix in final_state["fixes_applied"]:
            if fix.get("status") != "fixed":
                continue
            file_path = fix["file"]
            commit_msg = fix.get("commit_message", f"[AI-AGENT] Fix {file_path}")
            try:
                logger.info(f"run_agent: committing {file_path}")
                result = await client.commit_fix(
                    session_id=session_id,
                    file_path=file_path,
                    commit_message=commit_msg,
                    branch_name=branch_name,
                )
                if result.get("success"):
                    commit_hash = result.get("commit_hash")
                    total_commits += 1
            except Exception as e:
                logger.error(f"run_agent: commit failed for {file_path}: {e}")

    # ── 5. Timing & score ──
    time_taken = time.time() - start_time
    score = _calculate_score(total_commits, time_taken)

    # ── 6. Build result ──
    passed = final_state["passed"]
    total_fixes = len([f for f in final_state["fixes_applied"] if f["status"] == "fixed"])

    run_summary = {
        "repo_url": repo_url,
        "team_name": team_name,
        "team_leader_name": team_leader_name,
        "branch_name": branch_name,
        "total_failures": final_state.get("total_failures_detected", 0),
        "total_fixes": total_fixes,
        "final_status": "PASSED" if passed else "FAILED",
        "time_taken_seconds": round(time_taken, 2),
    }

    result = {
        "session_id": session_id,
        "status": "passed" if passed else ("partial_fix" if total_fixes > 0 else "failed"),
        "passed": passed,
        "iterations": final_state["iteration"],
        "message": "All tests passing." if passed else f"{len(final_state['errors'])} error(s) remain.",
        "run_summary": run_summary,
        "score_breakdown": score,
        "fixes_applied": final_state["fixes_applied"],
        "ci_timeline": final_state["ci_timeline"],
        "commit_hash": commit_hash,
        "branch_name": branch_name if commit_hash else None,
        "errors_remaining": final_state["errors"],
    }

    # ── 7. Write results.json ──
    try:
        results_path = Path("results.json")
        results_path.write_text(json.dumps(result, indent=2, default=str))
        logger.info(f"run_agent: results.json written to {results_path.resolve()}")
    except Exception as e:
        logger.error(f"run_agent: failed to write results.json: {e}")

    return result
