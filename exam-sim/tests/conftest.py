"""Shared fixtures for exam-sim tests.

* Puts the app root on sys.path so bare imports (``from bank import
  all_questions``) work exactly as they do inside the app.
* ``data_dir`` points the whole suite at a temp directory so no test can ever
  touch the real ~/.local/share/quantum-study/.  Since the migration onto
  ``common/`` every path is resolved **at call time** from
  ``QUANTUM_STUDY_DATA_DIR``, so setting the variable is the whole fixture —
  no module attribute has to be patched, and a subprocess a test spawns
  inherits the same redirect.
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

import common_path  # noqa: E402,F401  (puts the repo root on sys.path)

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


@pytest.fixture
def data_dir(tmp_path, monkeypatch):
    """Point the suite data directory at a temp dir for one test."""
    import persistence
    from common import schema

    root = tmp_path / "quantum-study"
    monkeypatch.setenv("QUANTUM_STUDY_DATA_DIR", str(root))
    # The "one backup per file per process" memo is global; without this the
    # second test in a process would skip its backup because the first test
    # already backed up a file of the same name in a different temp dir.
    schema.reset_session()
    persistence.clear_write_error()
    assert persistence.DATA_DIR == root, "config/persistence ignored the override"
    yield root
    schema.reset_session()
    persistence.clear_write_error()


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
