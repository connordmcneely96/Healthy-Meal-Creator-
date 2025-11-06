"""Wrapper utilities for working with OpenAI's text models."""
from __future__ import annotations

import logging
import os
from functools import lru_cache
from typing import Any, Dict

try:  # pragma: no cover - import guard
    from openai import OpenAI
    from openai.error import OpenAIError
except ImportError:  # pragma: no cover - optional dependency for tests
    OpenAI = None  # type: ignore

    class OpenAIError(Exception):
        """Fallback error when the OpenAI package is unavailable."""

LOGGER = logging.getLogger(__name__)
DEFAULT_MODEL = os.environ.get("OPENAI_DEFAULT_CHAT_MODEL", "gpt-3.5-turbo")


@lru_cache(maxsize=1)
def _client(api_key: str | None = None):
    """Return a cached OpenAI client instance."""

    if OpenAI is None:
        raise RuntimeError(
            "OpenAI Python client is not installed. Install the 'openai' package."
        )

    key = api_key or os.environ.get("OPENAI_API_KEY")
    if not key:
        raise RuntimeError(
            "OpenAI API key is not configured. Set OPENAI_API_KEY env variable."
        )
    return OpenAI(api_key=key)


def is_configured() -> bool:
    """Return True when an API key is available and client import succeeded."""

    return bool(os.environ.get("OPENAI_API_KEY")) and OpenAI is not None


def generate_meal_plan(prompt: str, *, model: str | None = None) -> Dict[str, Any]:
    """Generate a meal plan using a chat completion request."""

    model_name = model or DEFAULT_MODEL
    client = _client()
    try:
        completion = client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a nutrition assistant that produces structured"
                        " meal plans with shopping lists."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=float(os.environ.get("OPENAI_TEMPERATURE", "0.4")),
            max_tokens=int(os.environ.get("OPENAI_MAX_TOKENS", "512")),
        )
    except OpenAIError as exc:  # pragma: no cover - network errors are external
        LOGGER.error("OpenAI request failed: %s", exc)
        raise RuntimeError(f"Meal plan generation failed: {exc}") from exc

    message = completion.choices[0].message.content if completion.choices else ""
    return {
        "model": model_name,
        "prompt": prompt,
        "response": message,
        "usage": getattr(completion, "usage", None),
    }


__all__ = ["generate_meal_plan", "is_configured", "DEFAULT_MODEL"]
