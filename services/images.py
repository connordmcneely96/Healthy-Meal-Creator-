"""Tools for working with OpenAI's image APIs."""
from __future__ import annotations

import base64
import datetime as dt
import os
from pathlib import Path
from typing import Dict

try:  # pragma: no cover - optional dependency for tests
    from openai import OpenAI
    from openai.error import OpenAIError
except ImportError:  # pragma: no cover - optional dependency for tests
    OpenAI = None  # type: ignore

    class OpenAIError(Exception):
        pass

from .paths import DALLE_DIR, ensure_data_directories

DEFAULT_SIZE = os.environ.get("OPENAI_IMAGE_SIZE", "512x512")


def is_configured() -> bool:
    return bool(os.environ.get("OPENAI_API_KEY")) and OpenAI is not None


def _client() -> OpenAI:
    if OpenAI is None:
        raise RuntimeError(
            "OpenAI Python client is not installed. Install the 'openai' package."
        )
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise RuntimeError(
            "OpenAI API key is not configured. Set OPENAI_API_KEY env variable."
        )
    return OpenAI(api_key=key)


def generate_image(prompt: str, *, size: str | None = None) -> Dict[str, str]:
    """Generate an image using OpenAI's DALL·E API and persist it to disk."""

    ensure_data_directories()
    dalle_dir = DALLE_DIR
    dalle_dir.mkdir(parents=True, exist_ok=True)

    used_size = size or DEFAULT_SIZE
    filename = f"dalle_{dt.datetime.utcnow().strftime('%Y%m%dT%H%M%S')}.png"
    output_path = dalle_dir / filename

    try:
        client = _client()
        result = client.images.generate(
            model=os.environ.get("OPENAI_IMAGE_MODEL", "dall-e-2"),
            prompt=prompt,
            size=used_size,
            response_format="b64_json",
        )
    except OpenAIError as exc:  # pragma: no cover - network errors are external
        raise RuntimeError(f"Image generation failed: {exc}") from exc

    image_data = result.data[0].b64_json
    with open(output_path, "wb") as file:
        file.write(base64.b64decode(image_data))

    return {"path": str(output_path), "prompt": prompt, "size": used_size}


__all__ = ["generate_image", "is_configured"]
