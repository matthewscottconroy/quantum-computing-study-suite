"""Every file this app writes is versioned, migratable and backed up.

The suite now holds data you cannot regenerate — the mistake journal, the
confidence log, the flag queue, the session history.  Before ``common.schema``
there was no version marker anywhere, no migration path, and one bad write was
unrecoverable.  These tests pin the three properties that buy that back:

1. a version **sidecar** is written beside every file (and the data file keeps
   the exact shape ``coach.py`` and ``dashboard.py`` parse);
2. an older file is **migrated forward in memory** on read, and the file on
   disk is only restamped when something writes it;
3. a file written by a **newer build is refused, not overwritten**, and the
   rotating ``.bak`` copies let you get the previous state back.
"""
from __future__ import annotations

import json

import pytest

import common_path  # noqa: F401  (puts the repo root on sys.path)

import persistence
from common import journal, schema
from core.models import Attempt, GradeMode, Problem, SessionStats, Verdict

#: file name -> (the schema kind it is registered under, how to write one)
WRITERS = {
    "vqa_history.json": "history",
    "vqa_flagged.json": "flagged",
    "vqa_settings.json": "settings",
    "mistakes.json": "mistakes",
    "confidence.json": "confidence",
}


def _write_everything(item: str = "p1") -> None:
    """Touch every file this app owns, through its public API."""
    stats = SessionStats(total=1, correct=1)
    stats.attempts.append(Attempt(
        Problem(id=item, category="QAOA", difficulty="beginner", question="q",
                choices=["a", "b"], correct_index=0, grade_mode=GradeMode.MC),
        "A", 10, Verdict.CORRECT, "fb"))
    persistence.save_session(stats)
    persistence.toggle_flag(item)                    # a toggle: use a new id
    persistence.set_confidence_prompt_enabled(False)
    persistence.log_mistake(item, "QAOA", "q", "A", "B")
    persistence.log_confidence(item, "QAOA", 3, False)


@pytest.fixture(autouse=True)
def _fresh_backup_session():
    """common.schema backs a file up once per process; these tests want more."""
    schema.reset_session()
    yield
    schema.reset_session()


def test_every_file_this_app_writes_gets_a_version_sidecar(isolated_data_dir):
    _write_everything()
    for name, kind in WRITERS.items():
        sidecar = isolated_data_dir / f"{name}.schema.json"
        assert sidecar.is_file(), f"{name} has no schema sidecar"
        meta = json.loads(sidecar.read_text())
        assert meta["file"] == name
        assert meta["kind"] == kind
        assert meta["schema"] == schema.get(kind).version == 1
        assert meta["written_by"].startswith("common/")
        assert meta["updated"] > 0


def test_the_data_files_keep_the_shape_the_readers_require(isolated_data_dir):
    """The marker is a sidecar precisely so this stays true."""
    _write_everything()
    for name in ("vqa_history.json", "vqa_flagged.json", "mistakes.json",
                 "confidence.json"):
        data = json.loads((isolated_data_dir / name).read_text())
        assert isinstance(data, list), f"{name} must stay a plain JSON list"
        assert data, f"{name} was written empty"
    settings = json.loads((isolated_data_dir / "vqa_settings.json").read_text())
    assert settings == {"confidence_prompt": False}


def test_a_file_with_no_sidecar_is_treated_as_v1_and_read_normally(isolated_data_dir):
    """Files written before versioning existed are v1 files, not broken ones."""
    isolated_data_dir.mkdir(parents=True, exist_ok=True)
    legacy = [{"id": "old", "app": "vqa-trainer", "category": "QAOA",
               "question": "q", "your_answer": "a", "correct_answer": "b",
               "cause": None, "note": "", "timestamp": 1.0, "resolved": False}]
    (isolated_data_dir / "mistakes.json").write_text(json.dumps(legacy))
    assert not (isolated_data_dir / "mistakes.json.schema.json").exists()

    assert schema.stored_version(persistence.mistakes_path(), "mistakes") == 1
    assert persistence.load_mistakes() == legacy, "reading is never destructive"
    assert not (isolated_data_dir / "mistakes.json.schema.json").exists(), \
        "a read must not stamp the file"

    persistence.log_mistake("new", "QAOA", "q", "A", "B")
    assert (isolated_data_dir / "mistakes.json.schema.json").is_file()
    assert [r["id"] for r in persistence.load_mistakes()] == ["old", "new"]


def test_a_v2_file_is_migrated_forward_in_memory_and_restamped_on_write(
        isolated_data_dir, monkeypatch):
    """A registered migration runs on read; the file is only rewritten on write."""
    def _one_to_two(rows):
        return [{**r, "severity": r.get("severity", "normal")}
                for r in rows if isinstance(r, dict)]

    monkeypatch.setattr(
        schema, "_REGISTRY",
        {**schema._REGISTRY,
         "mistakes": schema.FileSchema("mistakes", version=2,
                                       migrations={1: _one_to_two})})

    isolated_data_dir.mkdir(parents=True, exist_ok=True)
    v1 = [{"id": "old", "app": "vqa-trainer", "category": "QAOA", "question": "q",
           "your_answer": "a", "correct_answer": "b", "cause": None, "note": "",
           "timestamp": 1.0, "resolved": False}]
    (isolated_data_dir / "mistakes.json").write_text(json.dumps(v1))

    rows = persistence.load_mistakes()
    assert rows[0]["severity"] == "normal", "migrated on read"
    assert json.loads((isolated_data_dir / "mistakes.json").read_text()) == v1, \
        "reading a v1 file leaves it a v1 file"

    persistence.log_mistake("new", "QAOA", "q", "A", "B")
    meta = json.loads((isolated_data_dir / "mistakes.json.schema.json").read_text())
    assert meta["schema"] == 2
    on_disk = json.loads((isolated_data_dir / "mistakes.json").read_text())
    assert on_disk[0]["severity"] == "normal" and len(on_disk) == 2


def test_a_newer_file_is_refused_rather_than_downgraded(isolated_data_dir):
    """A v3 file must not be rewritten with this build's v1 view of it."""
    journal.clear_write_error()
    persistence.log_mistake("ours", "QAOA", "q", "A", "B")
    before = (isolated_data_dir / "mistakes.json").read_text()

    sidecar = isolated_data_dir / "mistakes.json.schema.json"
    sidecar.write_text(json.dumps({"file": "mistakes.json", "kind": "mistakes",
                                   "schema": 3, "written_by": "common/9.9.9",
                                   "updated": 1.0}))

    persistence.log_mistake("later", "QAOA", "q", "A", "B")
    assert (isolated_data_dir / "mistakes.json").read_text() == before, \
        "the newer file was overwritten"
    err = journal.last_write_error()
    assert isinstance(err, schema.SchemaTooNewError)
    assert err.found == 3 and err.understood == 1
    assert persistence.last_write_error() is err
    journal.clear_write_error()
    assert persistence.last_write_error() is None


def test_history_and_settings_refuse_a_newer_file_without_raising(isolated_data_dir):
    """A refused write must never surface as an exception inside a session."""
    persistence.set_confidence_prompt_enabled(False)
    before = (isolated_data_dir / "vqa_settings.json").read_text()
    (isolated_data_dir / "vqa_settings.json.schema.json").write_text(json.dumps(
        {"file": "vqa_settings.json", "kind": "settings", "schema": 7}))

    persistence.set_confidence_prompt_enabled(True)          # must not raise
    assert (isolated_data_dir / "vqa_settings.json").read_text() == before

    _write_everything()                                       # nor here
    (isolated_data_dir / "vqa_history.json.schema.json").write_text(json.dumps(
        {"file": "vqa_history.json", "kind": "history", "schema": 7}))
    history_before = (isolated_data_dir / "vqa_history.json").read_text()
    _write_everything()
    assert (isolated_data_dir / "vqa_history.json").read_text() == history_before


def test_the_rotating_backup_keeps_the_state_each_run_started_from(isolated_data_dir):
    """One backup per file per run, three generations, restorable."""
    path = persistence.mistakes_path()

    persistence.log_mistake("run1", "QAOA", "q", "A", "B")
    assert not path.with_name(path.name + ".bak").exists(), \
        "nothing to back up before the very first write"
    run1 = path.read_text()

    schema.reset_session()                       # pretend a second run starts
    persistence.log_mistake("run2", "QAOA", "q", "A", "B")
    assert path.with_name(path.name + ".bak").read_text() == run1
    persistence.log_mistake("run2b", "QAOA", "q", "A", "B")
    assert path.with_name(path.name + ".bak").read_text() == run1, \
        "one backup per run, not one per write"
    run2 = path.read_text()

    schema.reset_session()                       # third run
    persistence.log_mistake("run3", "QAOA", "q", "A", "B")
    assert path.with_name(path.name + ".bak").read_text() == run2
    assert path.with_name(path.name + ".bak.1").read_text() == run1

    # And a corrupt file can be put back.
    path.write_text("half-written garba")
    assert persistence.load_mistakes() == []
    assert schema.restore_backup(path) is True
    assert [r["id"] for r in persistence.load_mistakes()] == ["run1", "run2", "run2b"]


def test_the_sidecars_are_invisible_to_the_apps_own_loaders(isolated_data_dir):
    """A directory full of sidecars and backups still reads as it always did."""
    _write_everything("p1")
    schema.reset_session()
    _write_everything("p2")

    names = {f.name for f in isolated_data_dir.iterdir()}
    assert any(n.endswith(".schema.json") for n in names)
    assert any(n.endswith(".bak") for n in names)

    assert len(persistence.load_mistakes()) == 2
    assert len(persistence.load_confidence()) == 2
    assert len(persistence._load_raw()) == 2
    assert persistence.load_flagged() == {"p1", "p2"}
    assert persistence.confidence_prompt_enabled() is False
