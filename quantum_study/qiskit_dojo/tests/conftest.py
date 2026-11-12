"""Fixtures for the qiskit-dojo tests.

The repository's root ``conftest.py`` provides ``qapp``, headless Qt and a
process-wide throwaway data directory.  This file narrows the data directory
to a fresh ``tmp_path`` per test and adds what only this app needs.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

APP_ROOT = Path(__file__).resolve().parent.parent


os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


_PERSISTENCE_PATHS = {
    "DATA_DIR": "",
    "HISTORY_FILE": "dojo_history.json",
    "FLAGGED_FILE": "dojo_flagged.json",
    "MISTAKES_FILE": "mistakes.json",
    "CONFIDENCE_FILE": "confidence.json",
    "SETTINGS_FILE": "dojo_settings.json",
}


@pytest.fixture
def data_dir(tmp_path, monkeypatch):
    """Point persistence (and config) at a temp dir. Fails closed if a
    constant vanished."""
    from quantum_study.qiskit_dojo import config
    from quantum_study.qiskit_dojo import persistence

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
    from quantum_study.qiskit_dojo.katas import all_katas
    return all_katas()
