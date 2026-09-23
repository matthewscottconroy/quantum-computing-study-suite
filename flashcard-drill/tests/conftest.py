"""Shared fixtures for flashcard-drill tests.

* Puts the app root on sys.path so bare imports (``from cards import all_cards``)
  work exactly as they do when the app runs, and runs the ``common_path`` shim
  so ``from common import journal`` resolves the same way the app's own modules
  make it resolve.
* Points QUANTUM_STUDY_DATA_DIR at a throwaway session directory *before* any
  app module is imported, and then, per test, at a fresh ``tmp_path``.  Since
  the migration to :mod:`common.datadir` every path in the app is resolved
  **at call time** from that one variable, so setting it is all a test needs —
  there are no module-level path constants left to relocate.
* Forces the offscreen Qt platform so the suite runs headless.
"""
from __future__ import annotations

import os
import pathlib
import shutil
import sys
import tempfile

import pytest

APP_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

import common_path  # noqa: E402,F401  (puts the repo root on sys.path)

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

# Always override (never inherit) so a developer's own QUANTUM_STUDY_DATA_DIR is
# never touched either.  Must happen before any app import.
_SESSION_DATA_DIR = pathlib.Path(tempfile.mkdtemp(prefix="flashcard-drill-tests-"))
os.environ["QUANTUM_STUDY_DATA_DIR"] = str(_SESSION_DATA_DIR)

REAL_DATA_DIR = pathlib.Path.home() / ".local" / "share" / "quantum-study"


def pytest_sessionfinish(session, exitstatus):
    shutil.rmtree(_SESSION_DATA_DIR, ignore_errors=True)


@pytest.fixture(autouse=True)
def data_dir(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> pathlib.Path:
    """Per-test data directory: one environment variable, resolved at call time."""
    from common import journal, schema

    target = tmp_path / "quantum-study"
    monkeypatch.setenv("QUANTUM_STUDY_DATA_DIR", str(target))
    # Per-process state that would otherwise leak between tests: "this file has
    # already been backed up once" and "the last write was refused".
    schema.reset_session()
    journal.clear_write_error()
    assert target != REAL_DATA_DIR        # belt and braces: never the real one
    return target


@pytest.fixture(scope="session")
def qapp():
    """One offscreen QApplication for the whole session."""
    from PyQt6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    yield app
