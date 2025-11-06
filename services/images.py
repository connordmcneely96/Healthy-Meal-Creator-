"""Tools for working with OpenAI's image APIs."""
from __future__ import annotations

import base64
import os
import time
from pathlib import Path
from typing import Dict

try:  # pragma: no cover - optional dependency for tests
    from openai import OpenAI
    from openai.error import OpenAIError
except ImportError:  # pragma: no cover - optional dependency for tests
    OpenAI = None  # type: ignore

    class OpenAIError(Exception):
        pass

from .paths import DALLE_DIR, build_artifact_path

DEFAULT_SIZE = os.environ.get("OPENAI_IMAGE_SIZE", "512x512")
DEFAULT_MODEL = os.environ.get("OPENAI_IMAGE_MODEL", "gpt-image-1")


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


def _write_png(data: str, output_path: Path) -> None:
    output_path.write_bytes(base64.b64decode(data))


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
            delay = backoff**attempt
            time.sleep(delay)
    assert last_error is not None
    raise RuntimeError(f"OpenAI image request failed after retries: {last_error}") from last_error


def generate_image(prompt: str, *, size: str | None = None) -> Dict[str, str]:
    """Generate an image using OpenAI's image API and persist it to disk."""

    used_size = size or DEFAULT_SIZE
    filename_stem = f"image-{time.strftime('%Y%m%dT%H%M%S')}"
    output_path = build_artifact_path(DALLE_DIR, filename_stem, ext="png")

    client = _client()

    def _request():
        return client.images.generate(
            model=DEFAULT_MODEL,
            prompt=prompt,
            size=used_size,
            response_format="b64_json",
        )

    try:
        result = _with_retries(_request)
    except RuntimeError as exc:  # pragma: no cover - network errors are external
        raise RuntimeError(f"Image generation failed: {exc}") from exc
    image_data = result.data[0].b64_json
    _write_png(image_data, output_path)

    return {"path": str(output_path), "prompt": prompt, "size": used_size}


def edit_image(
    image_path: str | Path,
    *,
    prompt: str,
    mask_path: str | Path | None = None,
    size: str | None = None,
) -> Dict[str, str]:
    """Edit an existing image using the image model and save the result."""

    used_size = size or DEFAULT_SIZE
    filename_stem = f"image-edit-{time.strftime('%Y%m%dT%H%M%S')}"
    output_path = build_artifact_path(DALLE_DIR, filename_stem, ext="png")

    image_path = Path(image_path)
    if not image_path.exists():
        raise FileNotFoundError(image_path)
    mask = Path(mask_path) if mask_path else None
    if mask and not mask.exists():
        raise FileNotFoundError(mask)

    client = _client()

    def _request():
        with image_path.open("rb") as image_file:
            files = {"image": image_file}
            mask_file = None
            if mask:
                mask_file = mask.open("rb")
                files["mask"] = mask_file
            try:
                return client.images.edit(
                    model=DEFAULT_MODEL,
                    prompt=prompt,
                    image=files.get("image"),
                    mask=files.get("mask"),
                    size=used_size,
                    response_format="b64_json",
                )
            finally:
                if mask_file:
                    mask_file.close()

    try:
        result = _with_retries(_request)
    except RuntimeError as exc:  # pragma: no cover - network errors are external
        raise RuntimeError(f"Image edit failed: {exc}") from exc
    image_data = result.data[0].b64_json
    _write_png(image_data, output_path)

    return {"path": str(output_path), "prompt": prompt, "size": used_size}


__all__ = ["generate_image", "edit_image", "is_configured"]
