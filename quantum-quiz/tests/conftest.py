"""Shared fixtures for quantum-quiz tests.

* Puts the app root on sys.path so bare imports (``from core.topics import TOPICS``)
  work exactly as they do when the app runs.
* Points QUANTUM_STUDY_DATA_DIR at a throwaway session directory *before* any
  app module is imported, and then gives every test its own empty ``tmp_path``
  directory (autouse, so it also covers the MainWindow smoke test).  Since the
  migration to ``common.datadir`` every data path is resolved **at call time**
  from that variable, so setting it is all a test has to do — there are no
  module-level path constants left to relocate.
* Resets ``common.schema``'s once-per-process backup bookkeeping between tests,
  so each test's first write backs up its own (empty) directory rather than
  being skipped because another test already backed up a same-named file.
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

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

# Always override (never inherit) so a developer's own QUANTUM_STUDY_DATA_DIR is
# never touched either.  Must happen before any app import.
_SESSION_DATA_DIR = pathlib.Path(tempfile.mkdtemp(prefix="quantum-quiz-tests-"))
os.environ["QUANTUM_STUDY_DATA_DIR"] = str(_SESSION_DATA_DIR)

REAL_DATA_DIR = pathlib.Path.home() / ".local" / "share" / "quantum-study"


def pytest_sessionfinish(session, exitstatus):
    shutil.rmtree(_SESSION_DATA_DIR, ignore_errors=True)


@pytest.fixture(autouse=True)
def data_dir(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> pathlib.Path:
    """Per-test data directory; every persistence path resolves into it."""
    import common_path  # noqa: F401  (puts the repo root on sys.path)
    from common import schema

    target = tmp_path / "quantum-study"
    monkeypatch.setenv("QUANTUM_STUDY_DATA_DIR", str(target))
    schema.reset_session()
    yield target
    schema.reset_session()


@pytest.fixture(scope="session")
def qapp():
    """One offscreen QApplication for the whole session."""
    from PyQt6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    yield app
