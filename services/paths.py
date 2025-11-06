"""Utility helpers for resolving project data directories and filenames."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

# Root of the repository (two levels up from this file)
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = PROJECT_ROOT / "data"

# Individual sub-directories where artifacts are stored.
MEAL_PLAN_DIR = DATA_ROOT / "meal_plan"
DALLE_DIR = DATA_ROOT / "dalle"
WHISPER_DIR = DATA_ROOT / "whisper"
LOG_DIR = DATA_ROOT / "logs"


def _expected_directories() -> Iterable[Path]:
    """Return all directories that should exist for the application."""

    return (
        MEAL_PLAN_DIR,
        DALLE_DIR,
        WHISPER_DIR,
        LOG_DIR,
    )


def ensure_data_directories() -> None:
    """Create all required data directories if they do not already exist."""

    for path in _expected_directories():
        path.mkdir(parents=True, exist_ok=True)


def get_data_directory(name: str) -> Path:
    """Return the data directory for a given logical name.

    Parameters
    ----------
    name:
        Supported names are "meal_plan", "dalle", "whisper" and "logs".

    Raises
    ------
    ValueError
        If an unsupported name is provided.
    """

    mapping = {
        "meal_plan": MEAL_PLAN_DIR,
        "dalle": DALLE_DIR,
        "whisper": WHISPER_DIR,
        "logs": LOG_DIR,
    }
    try:
        return mapping[name]
    except KeyError as exc:  # pragma: no cover - defensive branch
        raise ValueError(f"Unknown data directory '{name}'.") from exc


def safe_filename(name: str, *, ext: str | None = None, max_length: int = 80) -> str:
    """Return a filesystem-safe filename derived from ``name``.

    Non-alphanumeric characters are collapsed into hyphens and the resulting
    string is trimmed to ``max_length`` characters (excluding the extension).
    """

    normalized = re.sub(r"[^A-Za-z0-9]+", "-", name).strip("-") or "artifact"
    if max_length > 0:
        normalized = normalized[:max_length]
    if ext and not ext.startswith("."):
        ext = f".{ext}"
    return f"{normalized}{ext or ''}"


def build_artifact_path(directory: Path, stem: str, *, ext: str) -> Path:
    """Create a safe path inside ``directory`` using ``stem`` and ``ext``."""

    ensure_data_directories()
    directory.mkdir(parents=True, exist_ok=True)
    filename = safe_filename(stem, ext=ext)
    return directory / filename


# Ensure directories exist when the module is imported. This keeps the rest of
# the application simple.
ensure_data_directories()

__all__ = [
    "PROJECT_ROOT",
    "DATA_ROOT",
    "MEAL_PLAN_DIR",
    "DALLE_DIR",
    "WHISPER_DIR",
    "LOG_DIR",
    "ensure_data_directories",
    "get_data_directory",
    "safe_filename",
    "build_artifact_path",
]
