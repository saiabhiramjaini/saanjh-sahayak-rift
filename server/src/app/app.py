"""Application factory — builds and returns the FastAPI app."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.app.config import api_settings
from src.endpoints import health_router, agent_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle."""
    # --- Startup ---
    print(f"{api_settings.app_name} v{api_settings.version} starting...")
    print(f"EC2 Agent URL: {api_settings.ec2_agent_url}")
    print(f"LLM Model: {api_settings.llm_model}")
    print(f"Max iterations: {api_settings.max_iterations}")

    # Verify EC2 agent is reachable
    from src.services.ec2_client import EC2Client
    client = EC2Client()
    await client.ping()
    print("EC2 agent reachable")

    yield  # App is running

    # --- Shutdown ---
    print("Shutting down...")


def init_app() -> FastAPI:
    """Application factory."""
    app = FastAPI(
        title=api_settings.app_name,
        version=api_settings.version,
        debug=api_settings.debug,
        lifespan=lifespan,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=api_settings.cors_allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routers
    api_prefix = "/api/v1"
    app.include_router(health_router, prefix=api_prefix)
    app.include_router(agent_router, prefix=api_prefix)

    return app
