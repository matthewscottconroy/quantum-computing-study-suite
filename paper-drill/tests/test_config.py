"""config.py honours the suite-wide QUANTUM_STUDY_DATA_DIR override.

Since the migration to ``common.datadir`` the override is read **at call
time**, so these tests no longer reload the module: setting the environment
variable is enough, and a stale module constant can no longer exist to be out
of step with it.  That is the point of the change — the ten apps each froze
the directory at import time, which is why every app test used to need a
reload or a monkeypatched private name.
"""
from pathlib import Path

import pytest

import config

_FILE_HELPERS = ("history_file", "library_file", "flagged_file", "settings_file")


def test_data_dir_honours_env_override(tmp_path, monkeypatch):
    override = tmp_path / "override-data"
    monkeypatch.setenv("QUANTUM_STUDY_DATA_DIR", str(override))

    assert config.data_dir() == override
    for name in _FILE_HELPERS:
        assert getattr(config, name)().parent == override, name
    assert {getattr(config, n)().name for n in _FILE_HELPERS} == {
        "paper_history.json", "paper_library.json", "paper_flagged.json",
        "paper_settings.json",
    }
    # The two shared journals live in the same directory, under their
    # suite-wide names.
    assert config.mistakes_file() == override / "mistakes.json"
    assert config.confidence_file() == override / "confidence.json"


def test_override_takes_effect_without_reimport(tmp_path, monkeypatch):
    """Call-time resolution: change the variable, the next call follows it."""
    first, second = tmp_path / "one", tmp_path / "two"
    monkeypatch.setenv("QUANTUM_STUDY_DATA_DIR", str(first))
    assert config.history_file() == first / "paper_history.json"
    monkeypatch.setenv("QUANTUM_STUDY_DATA_DIR", str(second))
    assert config.history_file() == second / "paper_history.json"


@pytest.mark.parametrize("value", [None, "", "   "], ids=["unset", "empty", "blank"])
def test_data_dir_defaults_without_override(monkeypatch, value):
    if value is None:
        monkeypatch.delenv("QUANTUM_STUDY_DATA_DIR", raising=False)
    else:
        monkeypatch.setenv("QUANTUM_STUDY_DATA_DIR", value)
    default = Path.home() / ".local" / "share" / "quantum-study"
    assert config.data_dir() == default
    for name in _FILE_HELPERS:
        assert getattr(config, name)().parent == default, name


def test_tilde_in_the_override_is_expanded(monkeypatch):
    monkeypatch.setenv("QUANTUM_STUDY_DATA_DIR", "~/scratch-paper-drill")
    assert config.data_dir() == Path.home() / "scratch-paper-drill"


def test_other_constants_unaffected_by_override(tmp_path, monkeypatch):
    monkeypatch.setenv("QUANTUM_STUDY_DATA_DIR", str(tmp_path))
    assert config.MODEL == "claude-sonnet-4-6"
    assert config.API_KEY_FILE == Path.home() / ".config" / "quantum-study" / "api_key.txt"
    assert config.APP_ID == "paper-drill"


def test_file_names_agree_with_the_suite_wide_table():
    """coach.py finds this app's files through common.datadir.APP_FILES, so a
    rename made in one place and not the other would orphan the file."""
    from common import datadir

    known = datadir.APP_FILES["paper-drill"]
    assert known["history"] == config.HISTORY_NAME
    assert known["flagged"] == config.FLAGGED_NAME
    assert known["library"] == config.LIBRARY_NAME
    assert known["settings"] == config.SETTINGS_NAME
    # and the check config.py runs at import time agrees
    config._check_app_files()
