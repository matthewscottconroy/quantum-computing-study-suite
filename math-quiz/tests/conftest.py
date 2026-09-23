"""Shared fixtures for math-quiz tests.

* Puts the app root on sys.path so bare imports (``from core.topics import TOPICS``)
  work exactly as they do when the app runs.
* Points QUANTUM_STUDY_DATA_DIR at a throwaway session directory *before* any
  app module is imported, and then, per test, at a fresh ``tmp_path``.  Since
  the migration to ``common/`` every path is resolved **at call time** from
  that one variable, so setting it is all a test has to do — there are no
  module-level path constants left to relocate.
* Forces the offscreen Qt platform so the suite runs headless.
"""
from __future__ import annotations

import os
import pathlib
import shutil
import sys
import tempfile

import pytest

import common_path  # noqa: F401  (puts the repo root on sys.path)

APP_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

# Always override (never inherit) so a developer's own QUANTUM_STUDY_DATA_DIR is
# never touched either.  Must happen before any app import.
_SESSION_DATA_DIR = pathlib.Path(tempfile.mkdtemp(prefix="math-quiz-tests-"))
os.environ["QUANTUM_STUDY_DATA_DIR"] = str(_SESSION_DATA_DIR)

REAL_DATA_DIR = pathlib.Path.home() / ".local" / "share" / "quantum-study"


def pytest_sessionfinish(session, exitstatus):
    shutil.rmtree(_SESSION_DATA_DIR, ignore_errors=True)


@pytest.fixture(autouse=True)
def data_dir(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> pathlib.Path:
    """Per-test data directory.  Everything resolves through the env var."""
    target = tmp_path / "quantum-study"
    monkeypatch.setenv("QUANTUM_STUDY_DATA_DIR", str(target))
    # common.schema backs a file up once per process and common.journal
    # remembers the last refused write; each test gets a clean slate so a
    # backup is taken (and asserted on) in the test that wants one, and a
    # refusal never leaks into the next test.
    from common import journal, schema
    schema.reset_session()
    journal.clear_write_error()
    yield target
    schema.reset_session()
    journal.clear_write_error()


@pytest.fixture(scope="session")
def qapp():
    """One offscreen QApplication for the whole session."""
    from PyQt6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    yield app
