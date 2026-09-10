"""Test bootstrap for vqa-trainer: app root on sys.path, headless Qt, temp persistence."""
from __future__ import annotations

import os
import pathlib
import sys

APP_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest  # noqa: E402


@pytest.fixture(autouse=True)
def isolated_data_dir(tmp_path, monkeypatch):
    """Redirect every persistence path constant into a throwaway directory."""
    import persistence

    data_dir = tmp_path / "quantum-study"
    monkeypatch.setenv("QUANTUM_STUDY_DATA_DIR", str(data_dir))
    monkeypatch.setattr(persistence, "DATA_DIR", data_dir)
    monkeypatch.setattr(persistence, "HISTORY_FILE", data_dir / "vqa_history.json")
    if hasattr(persistence, "_FLAGGED_FILE"):
        monkeypatch.setattr(persistence, "_FLAGGED_FILE", data_dir / "vqa_flagged.json")
    return data_dir


@pytest.fixture(scope="session")
def qapp():
    from PyQt6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    yield app
