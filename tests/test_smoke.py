from __future__ import annotations

import importlib.util
import logging

from services import logger, paths


PAGE_FILES = [
    "Home.py",
    "1_Meal_Plan.py",
    "2_Image_Studio.py",
    "3_Speech_Lab.py",
    "4_Gallery.py",
    "5_Settings.py",
    "components.py",
]


def test_streamlit_pages_importable():
    base_dir = paths.PROJECT_ROOT / "app"
    for filename in PAGE_FILES:
        module_name = f"app.{filename[:-3]}"
        spec = importlib.util.spec_from_file_location(module_name, base_dir / filename)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # type: ignore[union-attr]


def test_logger_writes_file(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "LOG_DIR", tmp_path / "logs")
    logger._LOGGERS.clear()
    logging.getLogger("test").handlers.clear()
    log = logger.get_logger("test")
    log.info("hello")
    log_file = paths.LOG_DIR / "app.log"
    assert log_file.exists()
    content = log_file.read_text()
    assert "hello" in content
