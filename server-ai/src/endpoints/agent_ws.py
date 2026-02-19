"""WebSocket endpoint for real-time agent pipeline streaming."""

import json
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from src.runner.streaming_runner import run_streaming

logger = logging.getLogger("rift_server")

router = APIRouter(tags=["Agent WebSocket"])


@router.websocket("/agent/ws")
async def agent_websocket(websocket: WebSocket):
    """
    Real-time pipeline streaming over WebSocket.

    Protocol
    --------
    1. Client connects and sends a single JSON message with the pipeline config:
       ``{ repo_url, language, install_command, test_command, branch, branch_name, max_iterations }``
    2. Server streams events back as JSON messages:
       - ``{ type: "step", step, status }``                   — pipeline step status change
       - ``{ type: "log", line, ts }``                        — build log line
       - ``{ type: "iteration", iteration, total, status }``  — iteration result
       - ``{ type: "fix", fix: {...} }``                      — fix applied/failed
       - ``{ type: "complete", result: {...} }``              — final result
       - ``{ type: "error", message }``                       — fatal error
    3. Server closes the connection after ``complete`` or ``error``.
    """
    await websocket.accept()
    logger.info("[WS] Client connected")

    try:
        raw = await websocket.receive_text()
        config = json.loads(raw)
        logger.info(f"[WS] Config received: repo_url={config.get('repo_url')}")

        async def send_event(event: dict) -> None:
            try:
                await websocket.send_json(event)
            except Exception as exc:
                logger.warning(f"[WS] send failed: {exc}")

        result = await run_streaming(
            repo_url=config["repo_url"],
            language=config.get("language", "nodejs"),
            install_command=config.get("install_command"),
            test_command=config.get("test_command"),
            branch=config.get("branch", "main"),
            branch_name=config.get("branch_name"),
            max_iterations=config.get("max_iterations"),
            session_id=config.get("session_id"),
            github_token=config.get("github_token"),
            log=send_event,
        )

        await websocket.send_json({"type": "complete", "result": result})
        logger.info(f"[WS] Pipeline complete: passed={result.get('passed')}")

    except WebSocketDisconnect:
        logger.info("[WS] Client disconnected")
    except json.JSONDecodeError as exc:
        logger.error(f"[WS] Invalid JSON from client: {exc}")
        try:
            await websocket.send_json({"type": "error", "message": "Invalid JSON config"})
        except Exception:
            pass
    except Exception as exc:
        logger.error(f"[WS] Unhandled error: {exc}", exc_info=True)
        try:
            await websocket.send_json({"type": "error", "message": str(exc)})
        except Exception:
            pass
    finally:
        try:
            await websocket.close()
        except Exception:
            pass
