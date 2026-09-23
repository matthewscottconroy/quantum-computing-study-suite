"""``common.datadir`` — one rule for where the suite's data lives.

The point of the extraction is that the directory is resolved **at call time**.
Ten module-level constants, frozen at import, are what forced every app test to
monkeypatch a different private name; these tests assert the new behaviour is
the one that makes ``monkeypatch.setenv`` sufficient.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from common import datadir


# ---------------------------------------------------------------------------
# Resolution
# ---------------------------------------------------------------------------

def test_override_is_honoured(monkeypatch, tmp_path):
    monkeypatch.setenv(datadir.ENV_VAR, str(tmp_path))
    assert datadir.data_dir() == tmp_path


def test_default_is_local_share_quantum_study(monkeypatch, tmp_path):
    monkeypatch.delenv(datadir.ENV_VAR, raising=False)
    monkeypatch.setattr(Path, "home", staticmethod(lambda: tmp_path))
    assert datadir.data_dir() == tmp_path / ".local" / "share" / "quantum-study"
    assert datadir.data_dir() == datadir.default_data_dir()


def test_blank_override_is_no_override(monkeypatch, tmp_path):
    """Two of the ten copies stripped the value; eight did not, and made a
    directory literally named " "."""
    monkeypatch.setattr(Path, "home", staticmethod(lambda: tmp_path))
    for blank in ("", " ", "\t", "  \n "):
        monkeypatch.setenv(datadir.ENV_VAR, blank)
        assert datadir.data_dir() == datadir.default_data_dir(), repr(blank)


def test_tilde_in_override_is_expanded(monkeypatch, tmp_path):
    """Three of the ten expanded it; seven made a directory called "~".

    ``Path.expanduser`` reads ``$HOME`` (via ``os.path.expanduser``) rather
    than ``Path.home()``, so this test sets the variable itself.
    """
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv(datadir.ENV_VAR, "~/scratch")
    assert datadir.data_dir() == tmp_path / "scratch"
    assert "~" not in str(datadir.data_dir())


def test_resolution_happens_at_call_time(monkeypatch, tmp_path):
    """The whole reason for the extraction: no frozen module constant."""
    first, second = tmp_path / "a", tmp_path / "b"
    monkeypatch.setenv(datadir.ENV_VAR, str(first))
    assert datadir.data_dir() == first
    monkeypatch.setenv(datadir.ENV_VAR, str(second))
    assert datadir.data_dir() == second, "the directory was cached at import"


def test_data_dir_creates_nothing(monkeypatch, tmp_path):
    target = tmp_path / "not-yet"
    monkeypatch.setenv(datadir.ENV_VAR, str(target))
    datadir.data_dir()
    assert not target.exists(), "a read-only caller must not create the dir"


def test_ensure_data_dir_creates_it(monkeypatch, tmp_path):
    target = tmp_path / "deep" / "nested"
    monkeypatch.setenv(datadir.ENV_VAR, str(target))
    assert datadir.ensure_data_dir() == target
    assert target.is_dir()
    datadir.ensure_data_dir()               # idempotent
    assert target.is_dir()


# ---------------------------------------------------------------------------
# File helpers
# ---------------------------------------------------------------------------

def test_data_file_and_journal_paths(monkeypatch, tmp_path):
    monkeypatch.setenv(datadir.ENV_VAR, str(tmp_path))
    assert datadir.data_file("x.json") == tmp_path / "x.json"
    assert datadir.mistakes_file() == tmp_path / "mistakes.json"
    assert datadir.confidence_file() == tmp_path / "confidence.json"


@pytest.mark.parametrize("bad", ["", ".", "..", "a/b.json", "a\\b.json",
                                 "/etc/passwd"])
def test_data_file_rejects_a_path(bad):
    """A data file outside the data directory is never intended."""
    with pytest.raises(ValueError):
        datadir.data_file(bad)


def test_app_file_names_match_the_apps_on_disk(monkeypatch, tmp_path):
    """APP_FILES is a record of what the apps write, so it has to be right."""
    monkeypatch.setenv(datadir.ENV_VAR, str(tmp_path))
    repo = Path(__file__).resolve().parent.parent
    for app, kinds in datadir.APP_FILES.items():
        assert (repo / app).is_dir(), f"{app} is not an app directory"
        for kind, name in kinds.items():
            assert datadir.app_file(app, kind) == tmp_path / name
            assert name.endswith(".json")


def test_app_file_rejects_unknown_app_and_kind():
    with pytest.raises(KeyError):
        datadir.app_file("no-such-app", "history")
    with pytest.raises(KeyError):
        datadir.app_file("qec-trainer", "no-such-kind")


def test_apps_list_matches_the_repository():
    """Ten apps, each with a main.py — the same check CI's APPS step makes."""
    repo = Path(__file__).resolve().parent.parent
    on_disk = sorted(p.parent.name for p in repo.glob("*/main.py"))
    assert list(datadir.APPS) == on_disk
    assert len(datadir.APPS) == 10


def test_flashcard_keeps_its_legacy_flag_file_name():
    """flashcard-drill predates <prefix>_flagged.json; coach.py maps it by
    hand, so renaming it here would break the review queue."""
    assert datadir.APP_FILES["flashcard-drill"]["flagged"] == "flagged_cards.json"


def test_env_var_name_is_the_one_everything_else_uses():
    assert datadir.ENV_VAR == "QUANTUM_STUDY_DATA_DIR"
    repo = Path(__file__).resolve().parent.parent
    for name in ("coach.py", "dashboard.py", "launch.py"):
        assert datadir.ENV_VAR in (repo / name).read_text(encoding="utf-8")


def test_os_environ_is_read_not_a_snapshot(monkeypatch, tmp_path):
    """A child process that sets the variable after import still gets it."""
    monkeypatch.delenv(datadir.ENV_VAR, raising=False)
    monkeypatch.setattr(Path, "home", staticmethod(lambda: tmp_path))
    assert datadir.data_dir() == datadir.default_data_dir()
    os.environ[datadir.ENV_VAR] = str(tmp_path / "late")
    try:
        assert datadir.data_dir() == tmp_path / "late"
    finally:
        os.environ.pop(datadir.ENV_VAR, None)
