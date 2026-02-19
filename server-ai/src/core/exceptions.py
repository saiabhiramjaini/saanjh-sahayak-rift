"""Custom exceptions for RIFT Agent Server."""


class EC2AgentError(Exception):
    """Raised when ec2-agent returns an unexpected error."""
    status_code = 502  # Bad Gateway


class EC2AgentUnreachable(Exception):
    """Raised when ec2-agent cannot be reached."""
    status_code = 503


class SessionCreationError(Exception):
    """Raised when session creation fails."""
    status_code = 500


class AgentRunError(Exception):
    """Raised when the LangGraph agent run fails."""
    status_code = 500


class LLMError(Exception):
    """Raised when LLM call fails."""
    status_code = 500


class UnsupportedLanguageError(Exception):
    """Raised when requested language is not supported."""
    status_code = 422
