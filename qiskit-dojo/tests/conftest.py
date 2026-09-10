"""Shared fixtures for qiskit-dojo tests.

* Puts the app root on sys.path so bare imports (``from katas import all_katas``)
  work exactly as they do inside the app.
* ``data_dir`` redirects the persistence path constants into a temp dir so no
  test can ever touch the real ~/.local/share/quantum-study/.
* ``katas`` loads the bank once per process.
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
    "HISTORY_FILE": "dojo_history.json",
    "FLAGGED_FILE": "dojo_flagged.json",
}


@pytest.fixture
def data_dir(tmp_path, monkeypatch):
    """Point persistence (and config) at a temp dir. Fails closed if a
    constant vanished."""
    import config
    import persistence

    root = tmp_path / "quantum-study"
    monkeypatch.setenv("QUANTUM_STUDY_DATA_DIR", str(root))
    for module in (persistence, config):
        for name, filename in _PERSISTENCE_PATHS.items():
            if not hasattr(module, name):
                pytest.fail(f"{module.__name__}.{name} no longer exists - "
                            "update tests/conftest.py")
            monkeypatch.setattr(module, name, root / filename if filename else root)
        # Also redirect any other Path-valued *_FILE constant (except the API
        # key file, which is read-only) so no code path reached from a test
        # can write outside the temp dir.
        for name, value in list(vars(module).items()):
            if (name.endswith("_FILE") and isinstance(value, Path)
                    and name not in _PERSISTENCE_PATHS and name != "API_KEY_FILE"):
                monkeypatch.setattr(module, name, root / value.name)
    return root


@pytest.fixture(scope="session")
def katas():
    from katas import all_katas
    return all_katas()


_QAPP = None


@pytest.fixture(scope="session")
def qapp():
    """One offscreen QApplication for the whole test process."""
    global _QAPP
    from PyQt6.QtWidgets import QApplication

    _QAPP = QApplication.instance() or QApplication([])
    return _QAPP
