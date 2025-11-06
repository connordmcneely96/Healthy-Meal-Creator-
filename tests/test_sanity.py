from __future__ import annotations

from pathlib import Path

import importlib
import pkgutil

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_app_pages_exist():
    app_dir = REPO_ROOT / "app"
    expected = {
        "Home.py",
        "1_Meal_Plan.py",
        "2_Image_Studio.py",
        "3_Speech_Lab.py",
        "4_Gallery.py",
        "5_Settings.py",
        "components.py",
    }
    files = {path.name for path in app_dir.glob("*.py")}
    assert expected.issubset(files)


def test_services_modules_importable():
    for module_info in pkgutil.iter_modules(["services"]):
        importlib.import_module(f"services.{module_info.name}")
