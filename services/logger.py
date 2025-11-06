"""Application-level logging utilities."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from . import paths

_LOGGERS: dict[str, logging.Logger] = {}


def _configure_handler(log_dir: Path) -> logging.Handler:
    log_dir.mkdir(parents=True, exist_ok=True)
    handler = logging.FileHandler(log_dir / "app.log")
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    return handler


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Return a module-level logger that writes to ``data/logs/app.log``."""

    logger_name = name or "healthy_meal_creator"
    if logger_name in _LOGGERS:
        return _LOGGERS[logger_name]

    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = _configure_handler(paths.LOG_DIR)
        logger.addHandler(handler)
        logger.propagate = False

    _LOGGERS[logger_name] = logger
    return logger


__all__ = ["get_logger"]
