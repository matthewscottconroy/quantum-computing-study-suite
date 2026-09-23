"""Every file this app writes is versioned, migrated forward and backed up.

The suite now collects data that cannot be regenerated — an SM-2 schedule, a
mistake journal, confidence ratings, session history.  Before
:mod:`common.schema` there was no version marker anywhere, no migration path,
and one bad write was unrecoverable.  This module pins what the app now
guarantees for each of the six files it touches:

* a **sidecar** (``<file>.schema.json``) records the kind and the version that
  wrote it — a sidecar rather than a wrapper key, because ``coach.py`` and
  ``dashboard.py`` require the top level of these files to be a plain JSON
  list, and would read a wrapped file as *empty*;
* an **unmarked** file (everything written before this migration) is read as
  v1 and is never rewritten by merely reading it;
* a file from a **newer** build is refused, loudly at the call site and never
  by corrupting it;
* the state a session started from is **backed up** before that session's
  first write, three generations deep, and can be restored.
"""
from __future__ import annotations

import json

import pytest

import common_path  # noqa: F401  (puts the repo root on sys.path)

import persistence.review_store as rs
import persistence.schedule_store as schedule_store
import persistence.storage as storage
from common import schema
from core.models import CardResult, Rating, SessionStats

KINDS = {
    "history":    "flashcard_history.json",
    "schedule":   "flashcard_schedule.json",
    "settings":   "flashcard_settings.json",
    "flagged":    "flagged_cards.json",
    "mistakes":   "mistakes.json",
    "confidence": "confidence.json",
}


def _write_everything() -> None:
    """One write through every store this app owns."""
    stats = SessionStats(total=1, got_it=1)
    stats.results.append(CardResult("card_0", "Algorithms", Rating.GOT_IT))
    storage.save_session(stats)
    storage.toggle_flag("card_0")
    schedule_store.record_rating("card_0", "got_it")
    rs.set_confidence_enabled(False)
    rs.log_mistake("card_0", "Algorithms", "q", "a", "b")
    rs.log_confidence("card_0", "Algorithms", 3, False)


# ---------------------------------------------------------------------------
# The marker
# ---------------------------------------------------------------------------

def test_every_file_this_app_writes_is_registered_and_stamped(data_dir):
    _write_everything()
    for kind, name in KINDS.items():
        path = data_dir / name
        assert path.is_file(), f"{name} was not written"
        marker = json.loads((data_dir / f"{name}.schema.json").read_text())
        assert marker["file"] == name
        assert marker["kind"] == kind
        assert marker["schema"] == schema.get(kind).version == 1
        assert marker["written_by"].startswith("common/")
        assert marker["updated"] > 0


def test_the_marker_is_a_sidecar_so_the_data_files_keep_their_shape(data_dir):
    """A ``{"schema": 1, "rows": [...]}`` wrapper would read as empty in
    ``coach._load_list`` / ``dashboard._read_journal``; a list is a list."""
    _write_everything()
    for name in ("flashcard_history.json", "flagged_cards.json",
                 "mistakes.json", "confidence.json"):
        assert isinstance(json.loads((data_dir / name).read_text()), list)
    for name in ("flashcard_schedule.json", "flashcard_settings.json"):
        assert isinstance(json.loads((data_dir / name).read_text()), dict)


def test_a_file_written_before_versioning_is_read_as_v1_and_left_alone(data_dir):
    """The migration introduced the sidecar without changing any format."""
    data_dir.mkdir(parents=True, exist_ok=True)
    legacy = data_dir / "flashcard_history.json"
    legacy.write_text(json.dumps([{"total": 2, "got_it": 2, "unsure": 0,
                                   "missed": 0, "timestamp": 1.0,
                                   "results": []}]))
    assert not (data_dir / "flashcard_history.json.schema.json").exists()

    before = legacy.read_bytes()
    assert schema.stored_version(legacy, "history") == 1
    assert len(storage._load_raw()) == 1                 # read: no rewrite
    assert legacy.read_bytes() == before
    assert not (data_dir / "flashcard_history.json.schema.json").exists()

    storage.save_session(SessionStats(total=1, got_it=1))  # the next write stamps it
    assert (data_dir / "flashcard_history.json.schema.json").is_file()
    assert len(storage._load_raw()) == 2


# ---------------------------------------------------------------------------
# Migration forward
# ---------------------------------------------------------------------------

@pytest.fixture
def history_v2():
    """Register a v2 ``history`` schema for the duration of one test."""
    original = schema.get("history")

    def one_to_two(sessions):
        return [{**s, "migrated": True} for s in sessions if isinstance(s, dict)]

    schema.register(schema.FileSchema("history", version=2,
                                      migrations={1: one_to_two}), replace=True)
    try:
        yield
    finally:
        schema.register(original, replace=True)


def test_an_older_file_is_migrated_forward_in_memory_then_stamped(data_dir, history_v2):
    data_dir.mkdir(parents=True, exist_ok=True)
    path = data_dir / "flashcard_history.json"
    path.write_text(json.dumps([{"total": 1, "got_it": 1, "unsure": 0,
                                 "missed": 0, "timestamp": 1.0, "results": []}]))

    sessions = storage._load_raw()
    assert sessions[0]["migrated"] is True               # migrated on read
    assert "migrated" not in json.loads(path.read_text())[0]   # file untouched

    storage.save_session(SessionStats(total=1, got_it=1))
    assert schema.read_meta(path)["schema"] == 2         # stamped on write
    assert json.loads(path.read_text())[0]["migrated"] is True


# ---------------------------------------------------------------------------
# A newer file is refused, not corrupted
# ---------------------------------------------------------------------------

def _mark_newer(data_dir, name: str, kind: str) -> None:
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / f"{name}.schema.json").write_text(json.dumps(
        {"file": name, "kind": kind, "schema": 99,
         "written_by": "common/99.0.0", "updated": 1.0}))


def test_a_newer_history_is_refused_rather_than_overwritten(data_dir):
    _write_everything()
    before = (data_dir / "flashcard_history.json").read_bytes()
    _mark_newer(data_dir, "flashcard_history.json", "history")

    with pytest.raises(schema.SchemaTooNewError):
        storage.save_session(SessionStats(total=1, got_it=1))
    assert (data_dir / "flashcard_history.json").read_bytes() == before


def test_a_newer_journal_is_refused_and_reported_not_raised(data_dir):
    """A drill must not crash — the write returns "nothing happened" and says why."""
    _write_everything()
    before = (data_dir / "mistakes.json").read_bytes()
    _mark_newer(data_dir, "mistakes.json", "mistakes")

    assert rs.log_mistake("card_1", "Algorithms", "q", "a", "b") is None
    assert (data_dir / "mistakes.json").read_bytes() == before
    err = rs.last_write_error()
    assert isinstance(err, schema.SchemaTooNewError)
    assert err.found == 99 and err.understood == 1
    # …and the rows already there are still readable.
    assert [e["id"] for e in rs.load_mistakes()] == ["card_0"]


def test_a_newer_settings_file_is_refused_and_the_preference_survives(data_dir):
    rs.set_confidence_enabled(False)
    _mark_newer(data_dir, "flashcard_settings.json", "settings")
    assert rs.set_confidence_enabled(True) is False      # refused, not raised
    assert rs.confidence_enabled() is False              # the file is unchanged


def test_a_newer_flag_file_is_refused_and_the_button_can_say_so(data_dir):
    storage.toggle_flag("card_0")
    before = (data_dir / "flagged_cards.json").read_bytes()
    _mark_newer(data_dir, "flagged_cards.json", "flagged")

    with pytest.raises(schema.SchemaError):
        storage.toggle_flag("card_1")
    assert (data_dir / "flagged_cards.json").read_bytes() == before
    assert storage.load_flagged() == {"card_0"}


def test_a_newer_schedule_is_refused_without_interrupting_the_drill(data_dir):
    schedule_store.record_rating("card_0", "got_it")
    before = (data_dir / "flashcard_schedule.json").read_bytes()
    _mark_newer(data_dir, "flashcard_schedule.json", "schedule")

    assert schedule_store.record_rating("card_1", "got_it") is None
    assert (data_dir / "flashcard_schedule.json").read_bytes() == before


# ---------------------------------------------------------------------------
# Backups
# ---------------------------------------------------------------------------

def test_the_state_a_session_started_from_is_backed_up_and_restorable(data_dir):
    path = data_dir / "flashcard_history.json"

    storage.save_session(SessionStats(total=1, got_it=1))       # session 1
    assert not path.with_suffix(".json.bak").exists()           # nothing to keep yet

    schema.reset_session()                                      # session 2
    storage.save_session(SessionStats(total=2, got_it=2))
    storage.save_session(SessionStats(total=3, got_it=3))       # same session: one backup
    backups = schema.backup_paths(path)
    assert backups[0].is_file() and not backups[1].exists()
    assert len(json.loads(backups[0].read_text())) == 1         # the pre-session state
    assert len(storage._load_raw()) == 3

    schema.reset_session()                                      # session 3
    storage.save_session(SessionStats(total=4, got_it=4))
    assert len(json.loads(backups[0].read_text())) == 3         # rotated
    assert len(json.loads(backups[1].read_text())) == 1

    assert schema.restore_backup(path) is True
    assert len(storage._load_raw()) == 3                        # yesterday's file back


def test_only_three_generations_are_kept(data_dir):
    path = data_dir / "flashcard_history.json"
    for i in range(6):
        schema.reset_session()
        storage.save_session(SessionStats(total=i + 1, got_it=i + 1))
    kept = [p for p in data_dir.iterdir() if ".bak" in p.name]
    assert sorted(p.name for p in kept) == [
        "flashcard_history.json.bak", "flashcard_history.json.bak.1",
        "flashcard_history.json.bak.2"]
    # Newest first: .bak is the state before the last write.
    assert len(json.loads(path.read_text())) == 6
    assert [len(json.loads(p.read_text())) for p in schema.backup_paths(path)] == [5, 4, 3]
