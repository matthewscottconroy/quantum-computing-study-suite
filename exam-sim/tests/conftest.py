"""Shared fixtures for exam-sim tests.

* Puts the app root on sys.path so bare imports (``from bank import
  all_questions``) work exactly as they do inside the app.
* ``data_dir`` redirects the persistence path constants into a temp dir so no
  test can ever touch the real ~/.local/share/quantum-study/. (config.py reads
  QUANTUM_STUDY_DATA_DIR once at import time, so the env var alone would be
  too late here — the fixture also patches the module attributes, and sets the
  env var for any subprocess a test may spawn.)
* ``questions`` loads the bank once per process.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

APP_ROOT = Path(__file__).resolve().parent.parent
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

_PERSISTENCE_PATHS = {
    "DATA_DIR": "",
    "HISTORY_FILE": "exam_history.json",
    "MISSED_FILE": "exam_missed.json",
}


@pytest.fixture
def data_dir(tmp_path, monkeypatch):
    """Point persistence at a temp dir. Fails closed if a constant vanished."""
    import persistence

    root = tmp_path / "quantum-study"
    monkeypatch.setenv("QUANTUM_STUDY_DATA_DIR", str(root))
    for name, filename in _PERSISTENCE_PATHS.items():
        if not hasattr(persistence, name):
            pytest.fail(f"persistence.{name} no longer exists - update tests/conftest.py")
        monkeypatch.setattr(persistence, name, root / filename if filename else root)
    # Defensive: also redirect any other Path-valued *_FILE constant that may
    # appear on the module later, so no code path reached from a test can write
    # outside the temp dir. (exam-sim deliberately has no persisted review-flag
    # file — see README "Full exam"; misses flow to the coach via exam_missed.json.)
    for name, value in list(vars(persistence).items()):
        if name.endswith("_FILE") and isinstance(value, Path) and name not in _PERSISTENCE_PATHS:
            monkeypatch.setattr(persistence, name, root / value.name)
    return root


@pytest.fixture(scope="session")
def questions():
    from bank import all_questions
    return all_questions()


_QAPP = None


@pytest.fixture(scope="session")
def qapp():
    """One offscreen QApplication for the whole test process."""
    global _QAPP
    from PyQt6.QtWidgets import QApplication

    _QAPP = QApplication.instance() or QApplication([])
    return _QAPP
