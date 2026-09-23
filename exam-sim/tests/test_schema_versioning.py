"""Schema versioning, forward migration and rotating backups, from exam-sim.

``common.schema`` is unit-tested in the root suite; what is asserted here is
that **every file exam-sim writes** actually goes through it:

* a sidecar ``<name>.schema.json`` is stamped beside each file — a sidecar and
  not a key inside the data, because ``coach._load_list`` and
  ``dashboard._read_journal`` require the top level to be a plain JSON list;
* a file with no sidecar (everything written before this migration) is read as
  v1 and is not disturbed;
* a file written by a *newer* build is refused, not overwritten, and the
  refusal is reported rather than raised into a running exam;
* the first write of a session rotates a backup, and a later one does not.
"""
from __future__ import annotations

import json

import pytest

import common_path  # noqa: F401  (puts the repo root on sys.path)

import persistence
from common import schema
from core.models import ExamAttempt, ExamResult, Question

#: file name -> (the schema kind it is stamped with, how to write it)
WRITERS = {
    "exam_history.json":  "history",
    "exam_missed.json":   persistence.MISSED_KIND,
    "exam_settings.json": "settings",
    "mistakes.json":      "mistakes",
    "confidence.json":    "confidence",
}


def _q(qid: str = "s2", section: str = "Sampler", correct: int = 1) -> Question:
    return Question(id=qid, section=section, question=f"Question {qid}?",
                    options=["opt-a", "opt-b", "opt-c", "opt-d"],
                    correct_index=correct, explanation="because",
                    difficulty="easy")


def _write_everything() -> None:
    result = ExamResult(mode="sprint",
                        attempts=[ExamAttempt(_q(), chosen_index=3)],
                        duration_secs=1.0)
    persistence.save_result(result)
    persistence.record_misses(result)
    persistence.record_mistakes(result)
    persistence.log_confidence("s2", "Sampler", 3, False)
    persistence.set_confidence_enabled(False)


# ── the sidecar ──────────────────────────────────────────────────────────────

def test_every_file_this_app_writes_is_stamped_with_its_schema(data_dir):
    _write_everything()
    for name, kind in WRITERS.items():
        assert (data_dir / name).is_file(), name
        meta = json.loads((data_dir / f"{name}.schema.json").read_text())
        assert meta["file"] == name
        assert meta["kind"] == kind
        assert meta["schema"] == schema.get(kind).version == 1
        assert meta["written_by"].startswith("common/")
        assert isinstance(meta["updated"], float)


def test_the_payload_itself_is_still_a_bare_json_list(data_dir):
    """coach.py / dashboard.py read these files; the marker must stay outside."""
    _write_everything()
    for name in ("exam_history.json", "exam_missed.json",
                 "mistakes.json", "confidence.json"):
        data = json.loads((data_dir / name).read_text())
        assert isinstance(data, list) and data, name
        assert all(isinstance(row, dict) for row in data), name
        assert not any("schema" in row for row in data), name
    assert isinstance(json.loads((data_dir / "exam_settings.json").read_text()), dict)


def test_a_file_written_before_versioning_reads_as_v1_and_is_left_alone(data_dir):
    data_dir.mkdir(parents=True)
    legacy = [{"timestamp": 1.0, "mode": "full", "total": 68, "correct": 50,
               "duration_secs": 9.0, "sections": {}}]
    (data_dir / "exam_history.json").write_text(json.dumps(legacy))

    assert schema.stored_version(data_dir / "exam_history.json", "history") == 1
    assert persistence.load_history() == legacy
    # reading is never destructive: no sidecar appears until something writes
    assert not (data_dir / "exam_history.json.schema.json").exists()


def test_an_old_file_migrates_forward_when_a_migration_exists(data_dir):
    """The machinery, exercised with a synthetic v2 of the history schema."""
    data_dir.mkdir(parents=True)
    (data_dir / "exam_history.json").write_text(json.dumps([{"mode": "full"}]))
    original = schema.get("history")
    schema.register(schema.FileSchema(
        "history", version=2,
        migrations={1: lambda rows: [{**r, "migrated": True} for r in rows]}),
        replace=True)
    try:
        assert persistence.load_history() == [{"mode": "full", "migrated": True}]
        # and the rewrite stamps the new version
        persistence.save_result(ExamResult(mode="sprint"))
        meta = json.loads((data_dir / "exam_history.json.schema.json").read_text())
        assert meta["schema"] == 2
        rows = json.loads((data_dir / "exam_history.json").read_text())
        assert rows[0] == {"mode": "full", "migrated": True}
    finally:
        schema.register(original, replace=True)


# ── refusing a newer file ────────────────────────────────────────────────────

@pytest.mark.parametrize("name,kind", sorted(WRITERS.items()))
def test_a_newer_file_is_refused_rather_than_downgraded(data_dir, name, kind):
    data_dir.mkdir(parents=True)
    before = json.dumps([{"id": "keep", "app": "exam-sim", "resolved": False}]) \
        if name != "exam_settings.json" else json.dumps({"confidence_prompt": True})
    (data_dir / name).write_text(before)
    (data_dir / f"{name}.schema.json").write_text(json.dumps(
        {"file": name, "kind": kind, "schema": 99}))

    _write_everything()                      # must not raise

    assert (data_dir / name).read_text() == before, f"{name} was overwritten"
    err = persistence.last_write_error()
    assert isinstance(err, schema.SchemaTooNewError)
    assert "99" in str(err)


def test_the_app_keeps_working_after_a_refused_write(data_dir):
    data_dir.mkdir(parents=True)
    (data_dir / "mistakes.json").write_text("[]")
    (data_dir / "mistakes.json.schema.json").write_text(json.dumps(
        {"file": "mistakes.json", "kind": "mistakes", "schema": 99}))

    persistence.log_mistake(persistence.mistake_entry_for(_q(), 3))
    assert persistence.load_mistakes() == []          # nothing was written
    assert persistence.mistake_summary()["open"] == 0
    assert persistence.last_write_error() is not None
    persistence.clear_write_error()
    assert persistence.last_write_error() is None


# ── backups ──────────────────────────────────────────────────────────────────

def test_the_first_write_of_a_session_rotates_a_backup(data_dir):
    _write_everything()                                  # session 1: nothing to back up
    assert not (data_dir / "exam_history.json.bak").exists()
    first = (data_dir / "exam_history.json").read_text()

    schema.reset_session()                               # session 2
    persistence.save_result(ExamResult(mode="full"))
    assert (data_dir / "exam_history.json.bak").read_text() == first
    persistence.save_result(ExamResult(mode="full"))     # same session: no new backup
    assert (data_dir / "exam_history.json.bak").read_text() == first
    second = (data_dir / "exam_history.json").read_text()

    schema.reset_session()                               # session 3: generations age
    persistence.save_result(ExamResult(mode="sprint"))
    assert (data_dir / "exam_history.json.bak").read_text() == second
    assert (data_dir / "exam_history.json.bak.1").read_text() == first
    assert schema.restore_backup(data_dir / "exam_history.json", 1)
    assert (data_dir / "exam_history.json").read_text() == first


def test_a_backup_is_kept_for_the_shared_journal_too(data_dir):
    persistence.log_mistake(persistence.mistake_entry_for(_q("a"), 3))
    before = (data_dir / "mistakes.json").read_text()
    schema.reset_session()
    persistence.log_mistake(persistence.mistake_entry_for(_q("b"), 3))
    assert (data_dir / "mistakes.json.bak").read_text() == before
    assert [r["id"] for r in persistence.load_mistakes()] == ["a", "b"]
