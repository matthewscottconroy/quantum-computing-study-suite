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
    """Point every persistence path at a throwaway directory.

    Since the migration to ``common.datadir`` the location is resolved on every
    call rather than frozen into a module constant at import time, so setting
    the environment variable is the whole fixture — there are no private names
    left to patch.  (The subprocesses some tests spawn inherit it too.)

    ``common.schema`` keeps a process-wide "already backed up this file" set so
    a drill that logs two hundred rows makes one backup; it is cleared here so
    each test starts a fresh backup session.
    """
    import common_path  # noqa: F401
    from common import journal, schema

    data_dir = tmp_path / "quantum-study"
    monkeypatch.setenv("QUANTUM_STUDY_DATA_DIR", str(data_dir))
    schema.reset_session()
    journal.clear_write_error()
    yield data_dir
    schema.reset_session()
    journal.clear_write_error()


@pytest.fixture(scope="session")
def qapp():
    from PyQt6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    yield app
