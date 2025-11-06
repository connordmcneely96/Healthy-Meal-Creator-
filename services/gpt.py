"""Wrapper utilities for working with OpenAI's text models."""
from __future__ import annotations

import json
import logging
import os
import time
from functools import lru_cache
from typing import Any, Dict

try:  # pragma: no cover - import guard
    from openai import OpenAI
    from openai.error import OpenAIError
except ImportError:  # pragma: no cover - optional dependency for tests
    OpenAI = None  # type: ignore

    class OpenAIError(Exception):
        """Fallback error when the OpenAI package is unavailable."""

from .paths import MEAL_PLAN_DIR, build_artifact_path

LOGGER = logging.getLogger(__name__)
DEFAULT_MODEL = os.environ.get("OPENAI_DEFAULT_CHAT_MODEL", "gpt-4o-mini")


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


def _should_retry(exc: Exception) -> bool:
    status = getattr(exc, "status", None) or getattr(exc, "http_status", None)
    status_code = getattr(exc, "status_code", None)
    return any(code == 429 for code in (status, status_code))


def _with_retries(func, *, retries: int = 3, backoff: float = 1.5):
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            return func()
        except OpenAIError as exc:  # pragma: no cover - network errors are external
            last_error = exc
            if attempt == retries - 1 or not _should_retry(exc):
                break
            sleep_for = backoff**attempt
            LOGGER.warning("OpenAI rate limited, retrying in %.2fs", sleep_for)
            time.sleep(sleep_for)
    assert last_error is not None
    raise RuntimeError(f"OpenAI request failed after retries: {last_error}") from last_error


def is_configured() -> bool:
    """Return True when an API key is available and client import succeeded."""

    return bool(os.environ.get("OPENAI_API_KEY")) and OpenAI is not None


def _build_prompt(*, goal: str, calories: str | None, restrictions: str | None, meals: int) -> str:
    parts = [f"Goal: {goal.strip()}" or "General healthy eating"]
    if calories:
        parts.append(f"Target calories: {calories}")
    if restrictions:
        parts.append(f"Dietary preferences: {restrictions}")
    parts.append(f"Meals per day: {meals}")
    return "\n".join(parts)


def _parse_response(content: str) -> Dict[str, Any]:
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {"plan": content}


def create_meal_plan(
    *,
    goal: str,
    calories: str | None = None,
    restrictions: str | None = None,
    meals_per_day: int = 3,
    model: str | None = None,
) -> Dict[str, Any]:
    """Create a structured meal plan and persist it as Markdown.

    Returns a dictionary containing the parsed plan, markdown content, and the
    filesystem path where the plan was written.
    """

    model_name = model or DEFAULT_MODEL
    prompt = _build_prompt(
        goal=goal,
        calories=calories,
        restrictions=restrictions,
        meals=meals_per_day,
    )

    client = _client()

    def _request():
        return client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a nutrition assistant that produces structured meal plans. "
                        "Respond with JSON that includes keys 'summary', 'meals', and 'shopping_list'."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=float(os.environ.get("OPENAI_TEMPERATURE", "0.4")),
            max_tokens=int(os.environ.get("OPENAI_MAX_TOKENS", "900")),
        )

    try:
        completion = _with_retries(_request)
    except RuntimeError as exc:  # pragma: no cover - network errors are external
        raise RuntimeError(f"Meal plan generation failed: {exc}") from exc
    message = completion.choices[0].message.content if completion.choices else ""
    plan = _parse_response(message or "{}")

    markdown_lines = ["# Meal Plan", "", f"**Goal:** {goal}"]
    if calories:
        markdown_lines.append(f"**Calories:** {calories}")
    if restrictions:
        markdown_lines.append(f"**Preferences:** {restrictions}")
    markdown_lines.append("")
    markdown_lines.append("```json")
    markdown_lines.append(json.dumps(plan, indent=2, ensure_ascii=False))
    markdown_lines.append("```")
    markdown_content = "\n".join(markdown_lines)

    filename_stem = f"meal-plan-{time.strftime('%Y%m%dT%H%M%S')}"
    output_path = build_artifact_path(MEAL_PLAN_DIR, filename_stem, ext="md")
    output_path.write_text(markdown_content, encoding="utf-8")

    return {
        "model": model_name,
        "prompt": prompt,
        "plan": plan,
        "markdown": markdown_content,
        "path": str(output_path),
        "usage": getattr(completion, "usage", None),
    }


__all__ = ["create_meal_plan", "is_configured", "DEFAULT_MODEL"]
