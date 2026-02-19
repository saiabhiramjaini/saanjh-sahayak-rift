"""LLM client — Together AI for code repair."""

import logging

from together import Together

from src.app.config import api_settings
from src.core.exceptions import LLMError

logger = logging.getLogger("rift_server")

_client: Together | None = None


def _get_client() -> Together:
    """Lazy-initialised Together AI client."""
    global _client
    if _client is None:
        if not api_settings.together_api_key:
            raise LLMError("SERVER_TOGETHER_API_KEY is not set — cannot call LLM")
        _client = Together(api_key=api_settings.together_api_key)
    return _client


def _clean_output(text: str) -> str:
    """Strip markdown code fences returned by LLM."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines)
    return text.strip()


def ask_llm(prompt: str) -> str:
    """
    Send a code-repair prompt to the LLM and return the fixed code.

    Raises LLMError on failure.
    """
    client = _get_client()

    try:
        response = client.chat.completions.create(
            model=api_settings.llm_model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a senior software engineer fixing CI test failures. "
                        "Return ONLY the complete corrected file contents. "
                        "Do not include any explanation, markdown, or code fences."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=api_settings.llm_temperature,
            max_tokens=api_settings.llm_max_tokens,
        )

        content = response.choices[0].message.content
        logger.info(f"LLM response received ({len(content)} chars)")
        return _clean_output(content)

    except LLMError:
        raise
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        raise LLMError(f"LLM call failed: {e}")
