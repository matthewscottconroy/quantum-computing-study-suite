"""Test bootstrap for qec-trainer: app root on sys.path, headless Qt, temp data dir."""
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
    """Point the whole suite at a throwaway data directory.

    One environment variable is the whole fixture now.  ``common.datadir``
    resolves every path **at call time**, so nothing has to be reloaded and no
    private module constant has to be patched — which is exactly what the
    previous six ``monkeypatch.setattr`` lines existed to work around.
    """
    from common import schema

    data_dir = tmp_path / "quantum-study"
    monkeypatch.setenv("QUANTUM_STUDY_DATA_DIR", str(data_dir))
    # Backups are "once per file per process"; each test gets fresh paths, but
    # clear the ledger anyway so a test that reuses a path still gets one.
    schema.reset_session()
    yield data_dir
    schema.reset_session()


@pytest.fixture(scope="session")
def qapp():
    from PyQt6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    yield app
