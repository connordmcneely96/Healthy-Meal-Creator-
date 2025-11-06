from __future__ import annotations

from services import paths


def test_directories_exist(tmp_path, monkeypatch):
    # Ensure environment is isolated by pointing to a temp dir
    monkeypatch.setattr(paths, "DATA_ROOT", tmp_path)
    monkeypatch.setattr(paths, "MEAL_PLAN_DIR", tmp_path / "meal_plan")
    monkeypatch.setattr(paths, "DALLE_DIR", tmp_path / "dalle")
    monkeypatch.setattr(paths, "WHISPER_DIR", tmp_path / "whisper")
    monkeypatch.setattr(paths, "LOG_DIR", tmp_path / "logs")

    paths.ensure_data_directories()

    for directory in (paths.MEAL_PLAN_DIR, paths.DALLE_DIR, paths.WHISPER_DIR, paths.LOG_DIR):
        assert directory.exists()


def test_get_data_directory_valid_names():
    assert paths.get_data_directory("meal_plan") == paths.MEAL_PLAN_DIR
    assert paths.get_data_directory("dalle") == paths.DALLE_DIR
    assert paths.get_data_directory("whisper") == paths.WHISPER_DIR
    assert paths.get_data_directory("logs") == paths.LOG_DIR


def test_get_data_directory_invalid_name():
    try:
        paths.get_data_directory("invalid")
    except ValueError as exc:
        assert "Unknown data directory" in str(exc)
    else:  # pragma: no cover - safeguard
        raise AssertionError("Expected ValueError")
