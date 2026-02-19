"""Endpoints package."""

from src.endpoints.health import router as health_router
from src.endpoints.agent import router as agent_router

__all__ = ["health_router", "agent_router"]
