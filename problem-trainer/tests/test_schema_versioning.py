"""Schema versions, forward migration and rotating backups.

Every file this app writes — ``problems_history.json``,
``problems_flagged.json``, ``problems_settings.json`` and the two shared
journals — now goes through :mod:`common.schema`:

* a **sidecar** ``<name>.schema.json`` records the version.  It is a sidecar
  and not a key in the data because ``coach.py`` and ``dashboard.py`` require
  the top level of these files to be a plain JSON list; a wrapper object would
  make all three of their loaders read the file as empty;
* a file written by an **older** build is migrated forward in memory on read,
  and the file itself is only rewritten when something writes it;
* a file written by a **newer** build is *refused*: nothing is overwritten, the
  refusal is recorded in :func:`persistence.last_write_error` rather than
  raised into a drill, and the Setup screen shows it;
* before the first write of each process the previous contents are copied to
  ``<name>.bak``, ageing ``.bak`` -> ``.bak.1`` -> ``.bak.2``.
"""
from __future__ import annotations

import json

import pytest

import common_path  # noqa: F401  (puts the repo root on sys.path)

import persistence
from common import schema
from core.models import AttemptRecord, SessionStats

#: every file this app writes -> the schema kind that stamps it.
WRITTEN_FILES = {
    "problems_history.json":  "history",
    "problems_flagged.json":  "flagged",
    "problems_settings.json": "settings",
    "mistakes.json":          "mistakes",
    "confidence.json":        "confidence",
}


def _write_everything() -> None:
    persistence.save_session(SessionStats(
        attempts=[AttemptRecord("la_schmidt", "problem", 8.0, title="t")]))
    persistence.toggle_flag("la_schmidt", "Schmidt", "Linear Algebra & QM Math")
    persistence.set_confidence_prompt_enabled(False)
    persistence.log_mistake("p:a", "VQA", "Q", "wrong", "right")
    persistence.log_confidence("p:a", "VQA", 3, False)


def _meta(data_dir, name) -> dict:
    return json.loads((data_dir / f"{name}.schema.json").read_text())


# ---------------------------------------------------------------------------
# The sidecar
# ---------------------------------------------------------------------------

def test_every_file_this_app_writes_gets_a_version_sidecar(data_dir):
    _write_everything()
    for name, kind in WRITTEN_FILES.items():
        assert (data_dir / name).is_file(), name
        meta = _meta(data_dir, name)
        assert meta["file"] == name
        assert meta["kind"] == kind
        assert meta["schema"] == schema.get(kind).version == 1
        assert meta["written_by"].startswith("common/")
        assert isinstance(meta["updated"], float)


def test_the_data_files_themselves_are_unchanged_plain_json(data_dir):
    """The marker must stay invisible to coach.py / dashboard.py."""
    _write_everything()
    for name in WRITTEN_FILES:
        payload = json.loads((data_dir / name).read_text())
        if name == "problems_settings.json":
            assert isinstance(payload, dict)          # this app's own prefs
        else:
            assert isinstance(payload, list), name    # what the loaders require
            assert all(isinstance(row, dict) for row in payload), name
            assert not any("schema" in row for row in payload), name


def test_the_sidecars_do_not_collide_with_the_names_coach_globs(data_dir):
    _write_everything()
    assert sorted(p.name for p in data_dir.glob("*_history.json")) == [
        "problems_history.json"]              # launch.py's glob
    assert sorted(p.name for p in data_dir.glob("*_flagged.json")) == [
        "problems_flagged.json"]              # coach.py's _FLAGGED_GLOB


def test_reading_an_unmarked_file_neither_rewrites_nor_stamps_it(data_dir):
    """A file written before versioning existed is a v1 file; reading is safe."""
    data_dir.mkdir(parents=True)
    rows = [{"timestamp": 1.0, "total": 1, "avg_score": 5.0, "attempts": []}]
    (data_dir / "problems_history.json").write_text(json.dumps(rows))

    assert persistence.load_history() == rows
    assert not (data_dir / "problems_history.json.schema.json").exists()
    assert schema.stored_version(persistence.history_path(), "history") == 1
    assert json.loads((data_dir / "problems_history.json").read_text()) == rows


# ---------------------------------------------------------------------------
# Forward migration
# ---------------------------------------------------------------------------

@pytest.fixture
def history_v2():
    """Temporarily teach this process a v2 'history' schema with a migration."""
    original = schema.get("history")
    calls: list[int] = []

    def v1_to_v2(payload):
        calls.append(1)
        return [{**row, "version_note": "migrated"} for row in payload
                if isinstance(row, dict)]

    schema.register(schema.FileSchema("history", version=2,
                                      migrations={1: v1_to_v2}), replace=True)
    try:
        yield calls
    finally:
        schema.register(original, replace=True)


def test_an_older_file_migrates_forward_on_read_and_is_stamped_on_write(
        data_dir, history_v2):
    data_dir.mkdir(parents=True)
    rows = [{"timestamp": 1.0, "total": 1, "avg_score": 5.0, "attempts": []}]
    (data_dir / "problems_history.json").write_text(json.dumps(rows))

    migrated = persistence.load_history()
    assert history_v2 == [1], "the v1->v2 migration should have run once"
    assert migrated[0]["version_note"] == "migrated"
    # Reading is never destructive: the file is still the v1 one.
    assert json.loads((data_dir / "problems_history.json").read_text()) == rows

    persistence.save_session(SessionStats(
        attempts=[AttemptRecord("x", "problem", 4.0, title="t")]))
    assert _meta(data_dir, "problems_history.json")["schema"] == 2
    written = json.loads((data_dir / "problems_history.json").read_text())
    assert written[0]["version_note"] == "migrated"     # the migrated row persisted
    assert len(written) == 2


# ---------------------------------------------------------------------------
# Refusing a newer file
# ---------------------------------------------------------------------------

def _stamp(path, version: int) -> None:
    schema.sidecar_path(path).write_text(json.dumps(
        {"file": path.name, "kind": "history", "schema": version,
         "written_by": "common/99.0.0", "updated": 0.0}))


def test_a_newer_history_file_is_refused_not_overwritten(data_dir):
    data_dir.mkdir(parents=True)
    rows = [{"timestamp": 1.0, "total": 1, "avg_score": 5.0,
             "attempts": [], "field_from_the_future": True}]
    path = persistence.history_path()
    path.write_text(json.dumps(rows))
    _stamp(path, 99)

    persistence.save_session(SessionStats(
        attempts=[AttemptRecord("x", "problem", 4.0, title="t")]))

    assert json.loads(path.read_text()) == rows, "the newer file was overwritten"
    error = persistence.last_write_error()
    assert isinstance(error, schema.SchemaTooNewError)
    assert error.found == 99 and error.understood == 1
    assert "problems_history.json" in str(error)


def test_a_newer_journal_is_refused_and_the_drill_does_not_crash(data_dir):
    data_dir.mkdir(parents=True)
    rows = [{"id": "keepme", "app": "problem-trainer", "unknown": 1}]
    path = persistence.mistakes_path()
    path.write_text(json.dumps(rows))
    schema.sidecar_path(path).write_text(json.dumps(
        {"file": path.name, "kind": "mistakes", "schema": 7}))

    entry = persistence.log_mistake("p:a", "VQA", "Q", "w", "r")   # must not raise
    assert entry["id"] == "p:a"
    assert json.loads(path.read_text()) == rows
    assert isinstance(persistence.last_write_error(), schema.SchemaTooNewError)


def test_a_newer_flag_file_is_refused_and_toggle_reports_the_unchanged_state(data_dir):
    data_dir.mkdir(parents=True)
    path = persistence.flagged_path()
    rows = [{"id": "keepme", "label": "Keep", "category": "", "app": "problem-trainer",
             "timestamp": 0.0, "future_field": 1}]
    path.write_text(json.dumps(rows))
    schema.sidecar_path(path).write_text(json.dumps(
        {"file": path.name, "kind": "flagged", "schema": 4}))

    assert persistence.toggle_flag("newthing", "New", "VQA") is False
    assert persistence.unflag("keepme") is False
    assert json.loads(path.read_text()) == rows
    assert isinstance(persistence.last_write_error(), schema.SchemaTooNewError)


def test_the_setup_screen_surfaces_a_refused_write(main_window, data_dir, qapp):
    win = main_window
    setup = win._setup
    assert not setup._warning_lbl.isVisibleTo(setup)

    path = persistence.history_path()
    data_dir.mkdir(parents=True, exist_ok=True)
    path.write_text("[]")
    _stamp(path, 42)
    persistence.save_session(SessionStats(
        attempts=[AttemptRecord("x", "problem", 4.0, title="t")]))

    win._go_setup()
    qapp.processEvents()
    assert setup._warning_lbl.isVisibleTo(setup)
    assert "schema v42" in setup._warning_lbl.text()

    persistence.clear_write_error()
    win._go_setup()
    qapp.processEvents()
    assert not setup._warning_lbl.isVisibleTo(setup)


# ---------------------------------------------------------------------------
# Rotating backups
# ---------------------------------------------------------------------------

def test_the_first_write_of_a_session_backs_the_file_up_and_rotates(data_dir):
    path = persistence.history_path()

    def session(score: float) -> None:
        schema.reset_session()            # "a new process"
        persistence.save_session(SessionStats(
            attempts=[AttemptRecord("x", "problem", score, title="t")]))

    session(1.0)
    assert not path.with_suffix(".json.bak").exists(), "nothing existed to back up"

    session(2.0)
    bak = data_dir / "problems_history.json.bak"
    assert bak.is_file() and len(json.loads(bak.read_text())) == 1

    session(3.0)
    bak1 = data_dir / "problems_history.json.bak.1"
    assert len(json.loads(bak.read_text())) == 2
    assert len(json.loads(bak1.read_text())) == 1

    session(4.0)
    bak2 = data_dir / "problems_history.json.bak.2"
    assert [len(json.loads(p.read_text())) for p in (bak, bak1, bak2)] == [3, 2, 1]
    assert len(persistence.load_history()) == 4

    # Three generations, never four.
    assert not (data_dir / "problems_history.json.bak.3").exists()


def test_one_backup_per_session_however_many_writes(data_dir):
    for i in range(5):
        persistence.log_mistake(f"p:{i}", "VQA", "Q", "w", "r")
    assert not (data_dir / "mistakes.json.bak").exists()   # nothing to copy first

    schema.reset_session()
    for i in range(5, 10):
        persistence.log_mistake(f"p:{i}", "VQA", "Q", "w", "r")
    bak = data_dir / "mistakes.json.bak"
    assert bak.is_file()
    assert len(json.loads(bak.read_text())) == 5, "backed up once, not five times"
    assert not (data_dir / "mistakes.json.bak.1").exists()


def test_a_backup_can_be_restored_over_a_wrecked_file(data_dir):
    persistence.log_mistake("p:a", "VQA", "Q", "w", "r")
    schema.reset_session()
    persistence.log_mistake("p:b", "VQA", "Q", "w", "r")
    assert [e["id"] for e in persistence.app_mistakes()] == ["p:a", "p:b"]

    persistence.mistakes_path().write_text("{ truncated")
    assert persistence.load_mistakes() == []

    assert schema.restore_backup(persistence.mistakes_path()) is True
    assert [e["id"] for e in persistence.app_mistakes()] == ["p:a"]
