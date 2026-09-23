"""Test bootstrap for vqa-trainer: app root on sys.path, headless Qt, temp persistence."""
from __future__ import annotations

import os
import pathlib
import sys

APP_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import common_path  # noqa: E402,F401  (puts the repo root on sys.path)
import pytest  # noqa: E402


@pytest.fixture(autouse=True)
def isolated_data_dir(tmp_path, monkeypatch):
    """Point the whole app at a throwaway directory.

    ``QUANTUM_STUDY_DATA_DIR`` is the only thing that matters now: every path
    is resolved through ``common.datadir`` when it is used, not frozen at
    import.  The constants in ``config`` and ``persistence`` are an
    import-time snapshot of the same resolution, so they are redirected to the
    same directory — tests that assert on them (and ``test_config_env``'s
    subprocess probe) then still see the truth.
    """
    import config
    import persistence

    data_dir = tmp_path / "quantum-study"
    monkeypatch.setenv("QUANTUM_STUDY_DATA_DIR", str(data_dir))
    for mod, names in (
        (config, ("DATA_DIR", "HISTORY_FILE", "FLAGGED_FILE", "MISTAKES_FILE",
                  "CONFIDENCE_FILE", "SETTINGS_FILE")),
        (persistence, ("DATA_DIR", "HISTORY_FILE", "_FLAGGED_FILE", "MISTAKES_FILE",
                       "CONFIDENCE_FILE", "SETTINGS_FILE")),
    ):
        for name in names:
            current = getattr(mod, name, None)
            if current is None:
                continue
            target = data_dir if name == "DATA_DIR" else data_dir / current.name
            monkeypatch.setattr(mod, name, target)
    return data_dir


@pytest.fixture(autouse=True)
def _clean_common_module_state():
    """``common`` keeps two per-process globals; no test may inherit them.

    ``journal._LAST_WRITE_ERROR`` records the last refused write, and
    ``schema._BACKED_UP`` remembers which files this process has already
    backed up (one backup per file per run).  Both would otherwise leak from
    one test into the next.
    """
    from common import journal, schema

    journal.clear_write_error()
    schema.reset_session()
    yield
    journal.clear_write_error()
    schema.reset_session()


@pytest.fixture(scope="session")
def qapp():
    from PyQt6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    yield app
