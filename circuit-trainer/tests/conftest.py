"""Test bootstrap for circuit-trainer.

* Puts the app root on sys.path so bare imports (``from problems import generate``)
  work exactly as they do when ``main.py`` runs.
* Forces headless Qt.
* Redirects persistence to a per-test temp directory so no test can ever touch
  the real ``~/.local/share/quantum-study/``.
"""
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
    """Point every persistence path constant at a throwaway directory.

    persistence honours QUANTUM_STUDY_DATA_DIR, but only at import time, and the
    module is imported once per pytest process -- so the env var alone would
    not give each test its own directory.  Set it (for any subprocess the test
    spawns) AND patch the already-imported constants.
    """
    import persistence

    data_dir = tmp_path / "quantum-study"
    monkeypatch.setenv("QUANTUM_STUDY_DATA_DIR", str(data_dir))
    monkeypatch.setattr(persistence, "_DATA_DIR", data_dir)
    monkeypatch.setattr(persistence, "_HISTORY_FILE", data_dir / "trainer_history.json")
    if hasattr(persistence, "_FLAGGED_FILE"):
        monkeypatch.setattr(persistence, "_FLAGGED_FILE", data_dir / "trainer_flagged.json")
    return data_dir


@pytest.fixture(scope="session")
def qapp():
    from PyQt6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    yield app
