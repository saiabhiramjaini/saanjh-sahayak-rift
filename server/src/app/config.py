"""Main Server configuration — Pydantic BaseSettings."""

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class ApiSettings(BaseSettings):
    """Main server settings."""

    # ── App metadata ──
    app_name: str = Field(default="RIFT Agent Server", description="Application name")
    version: str = Field(default="1.0.0", description="Application version")
    debug: bool = Field(default=False, description="Enable debug mode")

    # ── Server ──
    host: str = Field(default="0.0.0.0", description="Bind host")
    port: int = Field(default=8000, description="Port to listen on")
    uvicorn_workers: int = Field(default=1, description="Uvicorn worker processes")
    reload: bool = Field(default=False, description="Auto-reload on code changes")

    # ── Logging ──
    log_level: str = Field(default="info", description="Log level")

    # ── CORS ──
    cors_allow_origins: list[str] = Field(
        default=["*"],
        description="Allowed CORS origins",
    )

    # ── EC2 Agent ──
    ec2_agent_url: str = Field(
        default="http://localhost:8001",
        description="Base URL of the EC2 agent service",
    )
    ec2_agent_api_key: str = Field(
        default="",
        description="API key for authenticating with EC2 agent",
    )

    # ── LLM (Groq) ──
    groq_api_key: str = Field(
        default="",
        description="Groq API key",
    )
    llm_model: str = Field(
        default="llama-3.3-70b-versatile",
        description="Groq model name",
    )
    llm_max_tokens: int = Field(default=4096, description="Max tokens per LLM call")
    llm_temperature: float = Field(default=0.2, description="LLM temperature")

    # ── Agent ──
    max_iterations: int = Field(
        default=5,
        description="Max LangGraph healing iterations",
    )

    @field_validator("log_level")
    @classmethod
    def lowercase_log_level(cls, v: str) -> str:
        return v.lower()

    model_config = {
        "env_prefix": "SERVER_",
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }


# Global singleton
api_settings = ApiSettings()