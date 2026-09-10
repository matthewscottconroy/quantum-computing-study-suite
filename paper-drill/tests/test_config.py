"""config.py honours the suite-wide QUANTUM_STUDY_DATA_DIR override.

Every test reloads ``config`` under a controlled environment and then reloads
it again with the process's original environment, so the module other tests
see is exactly what it was at import time.
"""
import importlib
from pathlib import Path

import pytest

import config

_FILE_CONSTANTS = ("HISTORY_FILE", "LIBRARY_FILE", "FLAGGED_FILE")


def _reload_with(monkeypatch, value):
    if value is None:
        monkeypatch.delenv("QUANTUM_STUDY_DATA_DIR", raising=False)
    else:
        monkeypatch.setenv("QUANTUM_STUDY_DATA_DIR", value)
    return importlib.reload(config)


def _restore(monkeypatch):
    monkeypatch.undo()
    importlib.reload(config)


def test_data_dir_honours_env_override(tmp_path, monkeypatch):
    override = tmp_path / "override-data"
    try:
        mod = _reload_with(monkeypatch, str(override))
        assert mod.DATA_DIR == override
        for name in _FILE_CONSTANTS:
            assert getattr(mod, name).parent == override, name
        assert {getattr(mod, n).name for n in _FILE_CONSTANTS} == {
            "paper_history.json", "paper_library.json", "paper_flagged.json",
        }
    finally:
        _restore(monkeypatch)


@pytest.mark.parametrize("value", [None, ""], ids=["unset", "empty"])
def test_data_dir_defaults_without_override(monkeypatch, value):
    try:
        mod = _reload_with(monkeypatch, value)
        assert mod.DATA_DIR == Path.home() / ".local" / "share" / "quantum-study"
        for name in _FILE_CONSTANTS:
            assert getattr(mod, name).parent == mod.DATA_DIR, name
    finally:
        _restore(monkeypatch)


def test_other_constants_unaffected_by_override(tmp_path, monkeypatch):
    try:
        mod = _reload_with(monkeypatch, str(tmp_path))
        assert mod.MODEL == "claude-sonnet-4-6"
        assert mod.API_KEY_FILE == Path.home() / ".config" / "quantum-study" / "api_key.txt"
        assert mod.APP_ID == "paper-drill"
    finally:
        _restore(monkeypatch)
