"""``common.schema`` — versioning, forward migration, refusal, backups.

The claim that has to be proved, not asserted: **the version marker does not
break the existing readers.**  ``coach.py`` and ``dashboard.py`` require the
top level of every data file to be a plain JSON list, so the marker lives in a
sidecar; the last group of tests runs the real loaders against a directory full
of sidecars and backups and checks they still see every row.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from common import journal, schema                  # noqa: E402
from common.jsonio import read_json_list            # noqa: E402


@pytest.fixture
def clean_session():
    schema.reset_session()
    yield
    schema.reset_session()


@pytest.fixture
def toy():
    """A synthetic kind at v3 with two migrations, so the machinery is really
    exercised — every real kind is at v1 with none, by design."""
    def one_to_two(rows):
        return [{**r, "added_in_v2": True} for r in rows if isinstance(r, dict)]

    def two_to_three(rows):
        out = []
        for r in rows:
            if not isinstance(r, dict):
                continue
            row = dict(r)
            row["renamed"] = row.pop("old_name", None)
            out.append(row)
        return out

    kind = schema.register(
        schema.FileSchema("toy", version=3, baseline=1,
                          migrations={1: one_to_two, 2: two_to_three}),
        replace=True)
    yield kind
    schema.unregister("toy")


# ---------------------------------------------------------------------------
# The registry
# ---------------------------------------------------------------------------

def test_the_suites_kinds_are_registered_at_v1():
    """The sidecar was introduced without changing any on-disk format, so an
    unmarked file *is* a v1 file and nothing has to be converted."""
    for kind in ("mistakes", "confidence", "flagged", "history", "settings",
                 "schedule"):
        s = schema.get(kind)
        assert (s.version, s.baseline, s.migrations) == (1, 1, {})
    assert set(schema.kinds()) >= {"mistakes", "confidence", "flagged"}


def test_unknown_kind_is_a_clear_error():
    with pytest.raises(schema.UnknownKindError) as exc:
        schema.get("nope")
    assert "registered:" in str(exc.value)


def test_registering_twice_needs_replace():
    with pytest.raises(ValueError):
        schema.register(schema.FileSchema("mistakes"))


def test_a_schema_with_a_gap_in_its_migrations_is_rejected():
    """Better to fail at import than to skip a step at runtime."""
    with pytest.raises(ValueError, match="v2->v3"):
        schema.FileSchema("gappy", version=3, migrations={1: lambda p: p})
    with pytest.raises(ValueError):
        schema.FileSchema("backwards", version=1, baseline=2)


# ---------------------------------------------------------------------------
# Version detection
# ---------------------------------------------------------------------------

def test_stored_version_of_an_unmarked_existing_file_is_the_baseline(tmp_path, toy):
    path = tmp_path / "toy.json"
    path.write_text("[]")
    assert schema.stored_version(path, "toy") == 1


def test_stored_version_of_a_file_that_does_not_exist_is_current(tmp_path, toy):
    assert schema.stored_version(tmp_path / "absent.json", "toy") == 3


def test_stored_version_reads_the_sidecar(tmp_path, toy):
    path = tmp_path / "toy.json"
    path.write_text("[]")
    schema.sidecar_path(path).write_text(json.dumps({"schema": 2}))
    assert schema.stored_version(path, "toy") == 2


@pytest.mark.parametrize("bad", [None, True, "2", 0, -1, {}, [2]])
def test_a_corrupt_sidecar_falls_back_to_the_baseline(tmp_path, toy, bad):
    path = tmp_path / "toy.json"
    path.write_text("[]")
    schema.sidecar_path(path).write_text(json.dumps({"schema": bad}))
    assert schema.stored_version(path, "toy") == 1


def test_sidecar_name(tmp_path):
    assert schema.sidecar_path(tmp_path / "mistakes.json").name == \
        "mistakes.json.schema.json"


# ---------------------------------------------------------------------------
# Migration
# ---------------------------------------------------------------------------

def test_load_versioned_migrates_forward_in_memory(tmp_path, toy, clean_session):
    path = tmp_path / "toy.json"
    path.write_text(json.dumps([{"id": "a", "old_name": "x"}]))
    rows = schema.load_versioned(path, "toy")
    assert rows == [{"id": "a", "added_in_v2": True, "renamed": "x"}]
    # ...and reading did not touch the file
    assert read_json_list(path) == [{"id": "a", "old_name": "x"}]
    assert schema.stored_version(path, "toy") == 1


def test_the_migration_lands_on_disk_at_the_next_write(tmp_path, toy, clean_session):
    path = tmp_path / "toy.json"
    path.write_text(json.dumps([{"id": "a", "old_name": "x"}]))
    rows = schema.load_versioned(path, "toy")
    schema.save_versioned(path, rows, "toy")
    assert schema.stored_version(path, "toy") == 3
    assert read_json_list(path)[0]["renamed"] == "x"


def test_migrate_payload_reports_the_number_of_steps(toy):
    payload, steps = schema.migrate_payload([{"id": "a"}], "toy", 1)
    assert steps == 2 and payload[0]["added_in_v2"] is True
    payload, steps = schema.migrate_payload([{"id": "a"}], "toy", 3)
    assert steps == 0


def test_a_v1_file_of_a_v1_kind_is_left_exactly_alone(tmp_path, clean_session):
    path = tmp_path / "mistakes.json"
    row = {"id": "a", "app": "qec-trainer", "surprise": 1}
    path.write_text(json.dumps([row]))
    assert schema.load_versioned(path, "mistakes") == [row]


# ---------------------------------------------------------------------------
# Refusing to downgrade
# ---------------------------------------------------------------------------

def test_writing_a_newer_file_is_refused_and_changes_nothing(tmp_path, clean_session):
    path = tmp_path / "mistakes.json"
    path.write_text(json.dumps([{"id": "keep", "app": "qec-trainer"}]))
    schema.sidecar_path(path).write_text(json.dumps({"schema": 7}))

    with pytest.raises(schema.SchemaTooNewError) as exc:
        schema.save_versioned(path, [], "mistakes")
    assert exc.value.found == 7 and exc.value.understood == 1
    assert "Refusing to write" in str(exc.value)
    assert read_json_list(path) == [{"id": "keep", "app": "qec-trainer"}]
    assert not list(tmp_path.glob("*.bak")), "a refusal must not even back up"


def test_reading_a_newer_file_is_allowed(tmp_path, clean_session):
    """Refuse to *write* it, never refuse to read it."""
    path = tmp_path / "mistakes.json"
    path.write_text(json.dumps([{"id": "a", "app": "x", "from_the_future": 1}]))
    schema.sidecar_path(path).write_text(json.dumps({"schema": 7}))
    assert schema.load_versioned(path, "mistakes")[0]["from_the_future"] == 1


def test_check_writable_is_silent_when_it_is(tmp_path, clean_session):
    path = tmp_path / "mistakes.json"
    path.write_text("[]")
    schema.check_writable(path, "mistakes")          # no exception


# ---------------------------------------------------------------------------
# Backups
# ---------------------------------------------------------------------------

def test_backup_rotation_keeps_three_generations(tmp_path, clean_session):
    path = tmp_path / "mistakes.json"
    for n in range(1, 6):
        path.write_text(json.dumps([{"gen": n}]))
        schema.reset_session(path)                   # a new "session" each time
        schema.save_versioned(path, [{"gen": n, "written": True}], "mistakes")

    newest, older, oldest = schema.backup_paths(path)
    assert newest.name == "mistakes.json.bak"
    assert older.name == "mistakes.json.bak.1"
    assert oldest.name == "mistakes.json.bak.2"
    # Generation 5's write backed up gen 5's pre-write contents, and so on.
    assert json.loads(newest.read_text()) == [{"gen": 5}]
    assert json.loads(older.read_text()) == [{"gen": 4}]
    assert json.loads(oldest.read_text()) == [{"gen": 3}]
    assert not (tmp_path / "mistakes.json.bak.3").exists()


def test_only_one_backup_per_session(tmp_path, clean_session):
    """A drill that logs two hundred rows makes one backup, not two hundred."""
    path = tmp_path / "mistakes.json"
    path.write_text(json.dumps([{"before": True}]))
    for i in range(20):
        schema.save_versioned(path, [{"row": i}], "mistakes")
    assert json.loads((tmp_path / "mistakes.json.bak").read_text()) == \
        [{"before": True}]
    assert not (tmp_path / "mistakes.json.bak.1").exists()


def test_no_backup_of_a_file_that_does_not_exist_yet(tmp_path, clean_session):
    path = tmp_path / "mistakes.json"
    schema.save_versioned(path, [{"first": True}], "mistakes")
    assert not list(tmp_path.glob("*.bak*"))


def test_restore_backup_brings_a_corrupt_file_back(tmp_path, clean_session):
    path = tmp_path / "mistakes.json"
    path.write_text(json.dumps([{"good": True}]))
    schema.save_versioned(path, [{"also_good": True}], "mistakes")
    path.write_text("{corrupt")
    assert read_json_list(path) == []
    assert schema.restore_backup(path) is True
    assert read_json_list(path) == [{"good": True}]


def test_restore_backup_of_a_missing_generation_is_false(tmp_path, clean_session):
    assert schema.restore_backup(tmp_path / "mistakes.json") is False
    assert schema.restore_backup(tmp_path / "mistakes.json", 2) is False


def test_backups_are_best_effort(tmp_path, clean_session, monkeypatch):
    """A full or read-only disk must not stop the write that matters."""
    path = tmp_path / "mistakes.json"
    path.write_text("[]")

    def boom(*a, **k):
        raise OSError("no space left on device")

    monkeypatch.setattr(schema.shutil, "copy2", boom)
    schema.save_versioned(path, [{"written": True}], "mistakes")
    assert read_json_list(path) == [{"written": True}]


# ---------------------------------------------------------------------------
# The sidecar does not break the existing readers
# ---------------------------------------------------------------------------

def _populated(tmp_path) -> Path:
    """A data directory written entirely through common.journal."""
    data = tmp_path / "quantum-study"
    data.mkdir()
    return data


def test_the_real_dashboard_and_coach_loaders_still_see_every_row(
        tmp_path, monkeypatch, clean_session):
    """The whole justification for the sidecar, executed.

    ``dashboard._read_journal``, ``dashboard._load`` and ``coach._load_list``
    all do ``return data if isinstance(data, list) else []`` — a wrapper object
    would make each of them read the journal as empty.
    """
    import coach
    import dashboard

    data = _populated(tmp_path)
    monkeypatch.setenv("QUANTUM_STUDY_DATA_DIR", str(data))
    journal.clear_write_error()

    for i in range(3):
        journal.log_mistake(journal.make_mistake_entry(
            f"item-{i}", "qec-trainer", "Gates", "q?", "wrong", "right",
            cause="misread", timestamp=1000.0 + i))
        journal.log_confidence(f"item-{i}", "qec-trainer", "Gates", 4, False,
                               timestamp=1000.0 + i)
    # A second session, so backups exist too.
    schema.reset_session()
    journal.log_mistake(journal.make_mistake_entry(
        "item-3", "qec-trainer", "Gates", "q?", "wrong", "right",
        timestamp=1003.0))

    # The sidecars and backups really are on disk beside the data files.
    assert (data / "mistakes.json.schema.json").is_file()
    assert (data / "confidence.json.schema.json").is_file()
    assert (data / "mistakes.json.bak").is_file()

    monkeypatch.setattr(dashboard, "DATA_DIR", data)
    monkeypatch.setattr(coach, "DATA_DIR", data)

    assert len(dashboard.load_mistakes()) == 4
    assert len(dashboard.load_confidence()) == 3
    assert len(coach.load_mistakes()) == 4
    assert len(coach.load_confidence()) == 3
    assert {e["cause"] for e in dashboard.load_mistakes()} == {"misread", None}

    # dashboard._load (the per-app history reader) is the third such reader.
    (data / "qec_history.json").write_text(json.dumps([{"total": 1}]))
    assert dashboard._load(data / "qec_history.json") == [{"total": 1}]


def test_a_sidecar_is_never_mistaken_for_a_data_file(tmp_path):
    """The readers open one exact file name; the sidecar is not it."""
    for name in ("mistakes.json", "confidence.json", "qec_flagged.json"):
        side = schema.sidecar_path(tmp_path / name)
        assert side.name != name
        assert side.name.endswith(".schema.json")
        for bak in schema.backup_paths(tmp_path / name):
            assert bak.name != name


def test_the_sidecar_records_what_wrote_it(tmp_path, clean_session):
    path = tmp_path / "mistakes.json"
    schema.save_versioned(path, [], "mistakes")
    meta = schema.read_meta(path)
    assert meta["file"] == "mistakes.json"
    assert meta["kind"] == "mistakes"
    assert meta["schema"] == 1
    assert meta["written_by"].startswith("common/")
    assert isinstance(meta["updated"], float)
