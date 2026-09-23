"""Mistake journal + confidence calibration: schema, helpers and headless UI.

The two files are the suite-wide contract (``mistakes.json`` /
``confidence.json``), so the schema is asserted field-for-field against a temp
data dir rather than by shape alone.
"""
from __future__ import annotations

import json
import time

import pytest

import common_path  # noqa: F401  (puts the repo root on sys.path)
from common import journal, schema

import persistence
from core.models import Attempt, GradeMode, Problem, Verdict


def _one_session():
    """One finished session, for the tests that need a history file on disk."""
    from core.models import SessionStats

    p = Problem(id="p1", category="Surface Code", difficulty="beginner",
                question="q", choices=["a", "b"], correct_index=0,
                grade_mode=GradeMode.AUTO)
    return SessionStats(total=1, correct=0,
                        attempts=[Attempt(p, "B", 0, Verdict.INCORRECT, "fb")])


MISTAKE_FIELDS = {
    "id", "app", "category", "question", "your_answer", "correct_answer",
    "cause", "note", "timestamp", "resolved",
}
CONFIDENCE_FIELDS = {"id", "app", "category", "confidence", "correct", "timestamp"}


# ── config honours QUANTUM_STUDY_DATA_DIR ─────────────────────────────────────

def test_config_resolves_every_file_under_the_env_override(tmp_path, monkeypatch):
    """Every path honours QUANTUM_STUDY_DATA_DIR, and re-reads it each time.

    No ``importlib.reload`` any more: ``common.datadir`` resolves at call time,
    so setting the variable is enough — which is the point of the extraction.
    """
    import config

    target = tmp_path / "elsewhere"
    monkeypatch.setenv("QUANTUM_STUDY_DATA_DIR", str(target))
    assert config.DATA_DIR == target
    for attr in ("HISTORY_FILE", "FLAGGED_FILE", "MISTAKES_FILE",
                 "CONFIDENCE_FILE", "SETTINGS_FILE"):
        assert getattr(config, attr).parent == target, attr
        assert getattr(persistence, attr).parent == target, attr
    assert config.MISTAKES_FILE.name == "mistakes.json"
    assert config.CONFIDENCE_FILE.name == "confidence.json"
    assert config.HISTORY_FILE.name == "qec_history.json"
    assert config.FLAGGED_FILE.name == "qec_flagged.json"
    assert config.SETTINGS_FILE.name == "qec_settings.json"
    # the API key lives in ~/.config and is deliberately not moved
    assert config.API_KEY_FILE.name == "api_key.txt"

    # …and moving the variable moves every path, with nothing reloaded.
    moved = tmp_path / "moved"
    monkeypatch.setenv("QUANTUM_STUDY_DATA_DIR", str(moved))
    assert config.DATA_DIR == moved and persistence.HISTORY_FILE.parent == moved


def test_config_default_is_unchanged_without_the_env_var(monkeypatch):
    import pathlib
    import config

    monkeypatch.delenv("QUANTUM_STUDY_DATA_DIR", raising=False)
    assert config.DATA_DIR == pathlib.Path.home() / ".local" / "share" / "quantum-study"
    assert persistence.MISTAKES_FILE == config.DATA_DIR / "mistakes.json"


def test_a_blank_override_is_no_override(monkeypatch):
    """`QUANTUM_STUDY_DATA_DIR=" "` used to make a directory literally named " "."""
    import pathlib
    import config

    monkeypatch.setenv("QUANTUM_STUDY_DATA_DIR", "   ")
    assert config.DATA_DIR == pathlib.Path.home() / ".local" / "share" / "quantum-study"


# ── Mistake journal ───────────────────────────────────────────────────────────

def test_mistake_entry_schema_field_for_field(isolated_data_dir):
    before = time.time()
    entry = persistence.make_mistake_entry(
        item_id="rep_distance", category="Repetition Code",
        question="What is the distance of the 3-qubit repetition code?",
        your_answer="B. 2", correct_answer="C. 3")
    persistence.log_mistake(entry)

    raw = json.loads((isolated_data_dir / "mistakes.json").read_text())
    assert isinstance(raw, list) and len(raw) == 1
    row = raw[0]
    assert set(row) == MISTAKE_FIELDS
    assert row["id"] == "rep_distance"
    assert row["app"] == "qec-trainer"
    assert row["category"] == "Repetition Code"
    assert row["question"] == "What is the distance of the 3-qubit repetition code?"
    assert row["your_answer"] == "B. 2"
    assert row["correct_answer"] == "C. 3"
    assert row["cause"] is None
    assert row["note"] == ""
    assert isinstance(row["timestamp"], float) and before <= row["timestamp"] <= time.time()
    assert row["resolved"] is False


def test_long_text_is_clipped_to_200_chars():
    row = persistence.make_mistake_entry("i", "c", "q" * 400, "a" * 400, "b" * 400)
    assert len(row["question"]) == len(row["your_answer"]) == len(row["correct_answer"]) == 200


def test_cause_is_validated_and_bad_values_never_lose_the_mistake():
    entry = persistence.make_mistake_entry("i", "c", "q", "a", "b", cause="nonsense")
    assert entry["cause"] is None
    persistence.log_mistake(entry)
    assert persistence.set_mistake_cause("i", "also-nonsense")["cause"] is None
    assert len(persistence.load_mistakes()) == 1
    for cause in persistence.MISTAKE_CAUSES:
        assert persistence.set_mistake_cause("i", cause)["cause"] == cause


def test_skip_then_categorise_then_resolve():
    persistence.log_mistake(persistence.make_mistake_entry(
        "stab_commute", "Stabilizer Formalism", "q", "A", "B"))
    assert [r["cause"] for r in persistence.load_mistakes()] == [None]   # skippable

    updated = persistence.set_mistake_cause("stab_commute", "knew_but_slipped", "read it twice")
    assert updated["cause"] == "knew_but_slipped" and updated["note"] == "read it twice"
    assert persistence.cause_counts() == {"knew_but_slipped": 1}
    assert [r["id"] for r in persistence.open_mistakes()] == ["stab_commute"]

    assert persistence.resolve_mistake("stab_commute") == 1
    assert persistence.resolve_mistake("stab_commute") == 0     # idempotent
    rows = persistence.load_mistakes()
    assert len(rows) == 1 and rows[0]["resolved"] is True
    assert rows[0]["cause"] == "knew_but_slipped"                # cause survives
    assert persistence.open_mistakes() == []


def test_missing_the_same_item_twice_keeps_both_rows():
    """A repeat is a second row, not an update.

    This app used to merge a re-log into the open row.  ``dashboard.py`` says
    why that is wrong in so many words — "a genuine second miss of the same
    item keeps its own entry, because repetition is exactly the signal" — and
    merging destroyed the count ``coach --mistakes`` reports.  Eight of the ten
    apps already appended; ``common.journal`` is the append.
    """
    persistence.log_mistake(persistence.make_mistake_entry("p", "C", "q", "A", "D"))
    persistence.set_mistake_cause("p", "misread", "slow down")
    persistence.log_mistake(persistence.make_mistake_entry("p", "C", "q", "B", "D"))

    rows = persistence.load_mistakes()
    assert [r["your_answer"] for r in rows] == ["A", "B"]      # both misses kept
    assert rows[0]["cause"] == "misread" and rows[0]["note"] == "slow down"
    assert rows[1]["cause"] is None                            # the new one is fresh

    # categorising now edits the newest open row, so causes do not pile up
    persistence.set_mistake_cause("p", "confused")
    rows = persistence.load_mistakes()
    assert [r["cause"] for r in rows] == ["misread", "confused"]
    assert persistence.cause_counts() == {"misread": 1, "confused": 1}

    # resolving clears every open row for the item at once
    assert persistence.resolve_mistake("p") == 2
    assert persistence.open_mistakes() == []
    assert [r["cause"] for r in persistence.load_mistakes()] == ["misread", "confused"]


def test_entries_from_other_apps_are_never_touched():
    persistence.save_mistakes([persistence.make_mistake_entry(
        "x", "C", "q", "a", "b", app="exam-sim")])
    persistence.log_mistake(persistence.make_mistake_entry("x", "C", "q", "a", "b"))
    persistence.set_mistake_cause("x", "confused")
    persistence.resolve_mistake("x")
    rows = persistence.load_mistakes()
    assert len(rows) == 2
    other = [r for r in rows if r["app"] == "exam-sim"][0]
    assert other["cause"] is None and other["resolved"] is False
    assert persistence.cause_counts() == {"confused": 1}
    assert persistence.cause_counts(app=None) == {"confused": 1}


# ── Confidence calibration ────────────────────────────────────────────────────

def test_confidence_entry_schema_field_for_field(isolated_data_dir):
    before = time.time()
    persistence.log_confidence("surf_mwpm", "Surface Code", 4, False)
    raw = json.loads((isolated_data_dir / "confidence.json").read_text())
    assert len(raw) == 1
    row = raw[0]
    assert set(row) == CONFIDENCE_FIELDS
    assert row["id"] == "surf_mwpm"
    assert row["app"] == "qec-trainer"
    assert row["category"] == "Surface Code"
    assert row["confidence"] == 4
    assert row["correct"] is False
    assert isinstance(row["timestamp"], float) and before <= row["timestamp"] <= time.time()


@pytest.mark.parametrize("bad", [None, 0, 5, -1, 9, "", "high", object()])
def test_skipped_or_invalid_confidence_records_nothing(bad):
    assert persistence.log_confidence("i", "c", bad, True) is None
    assert persistence.load_confidence() == []


def test_numeric_strings_are_accepted_leniently():
    assert persistence.log_confidence("i", "c", "3", True)["confidence"] == 3


def test_calibration_summary_finds_the_confidently_wrong():
    for correct in (True, True, False):
        persistence.log_confidence("a", "Steane Code", 4, correct)
    persistence.log_confidence("b", "Steane Code", 1, True)
    persistence.save_confidence(persistence.load_confidence() + [
        persistence.make_confidence_entry("z", "Other", 4, False, app="math-quiz")])
    # {"total", "correct"} — the suite-wide bucket names (this app said "n")
    assert persistence.calibration_summary() == {1: {"total": 1, "correct": 1},
                                                 4: {"total": 3, "correct": 2}}
    assert [r["id"] for r in persistence.confidently_wrong()] == ["a"]


# ── Robustness: missing, corrupt, non-list, capped ────────────────────────────

@pytest.mark.parametrize("junk", ["", "not json", "{}", "[1, 2, 3]", '"a string"', "null"])
def test_corrupt_files_read_as_empty_and_are_repaired_on_write(isolated_data_dir, junk):
    isolated_data_dir.mkdir(parents=True, exist_ok=True)
    (isolated_data_dir / "mistakes.json").write_text(junk)
    (isolated_data_dir / "confidence.json").write_text(junk)
    (isolated_data_dir / "qec_settings.json").write_text(junk)

    assert persistence.load_mistakes() == []
    assert persistence.load_confidence() == []
    assert persistence.load_settings() == {"confidence_prompt": True}
    assert persistence.set_mistake_cause("nope", "misread") is None
    assert persistence.resolve_mistake("nope") == 0

    persistence.log_mistake(persistence.make_mistake_entry("i", "c", "q", "a", "b"))
    persistence.log_confidence("i", "c", 2, True)
    assert len(persistence.load_mistakes()) == 1
    assert len(persistence.load_confidence()) == 1


def test_missing_files_and_missing_directory_are_fine(isolated_data_dir):
    assert not isolated_data_dir.exists()
    assert persistence.load_mistakes() == [] and persistence.load_confidence() == []
    assert persistence.open_mistakes() == [] and persistence.cause_counts() == {}
    assert persistence.calibration_summary() == {}
    persistence.log_mistake(persistence.make_mistake_entry("i", "c", "q", "a", "b"))
    assert (isolated_data_dir / "mistakes.json").exists()


def test_growth_is_capped_keeping_the_newest(monkeypatch, isolated_data_dir):
    monkeypatch.setattr(journal, "MISTAKES_MAX", 5)
    monkeypatch.setattr(journal, "CONFIDENCE_MAX", 5)
    assert persistence.MISTAKES_MAX == 5 and persistence.CONFIDENCE_MAX == 5
    for i in range(12):
        persistence.log_mistake(persistence.make_mistake_entry(
            f"p{i}", "c", "q", "a", "b", timestamp=1000.0 + i))
        persistence.log_confidence(f"p{i}", "c", 3, True, timestamp=1000.0 + i)
    assert [r["id"] for r in persistence.load_mistakes()] == [f"p{i}" for i in range(7, 12)]
    assert [r["id"] for r in persistence.load_confidence()] == [f"p{i}" for i in range(7, 12)]


def test_the_cap_never_trims_another_apps_rows(monkeypatch, isolated_data_dir):
    """The data-loss bug this app shipped: trimming the *merged* list.

    ``sorted(all_rows, key=timestamp)[-MAX:]`` deleted rows belonging to the
    other nine apps during a write to a file this app does not own.  Only our
    own rows may ever be dropped.
    """
    monkeypatch.setattr(journal, "MISTAKES_MAX", 4)
    foreign = [persistence.make_mistake_entry(
        f"x{i}", "C", "q", "a", "b", timestamp=1.0 + i, app="exam-sim")
        for i in range(3)]
    persistence.save_mistakes(foreign, app="exam-sim")

    for i in range(6):
        persistence.log_mistake(persistence.make_mistake_entry(
            f"p{i}", "c", "q", "a", "b", timestamp=1000.0 + i))

    rows = persistence.load_mistakes()
    assert [r["id"] for r in rows if r["app"] == "exam-sim"] == ["x0", "x1", "x2"]
    assert [r["id"] for r in rows if r["app"] == "qec-trainer"] == ["p5"]


def test_writes_are_atomic_and_leave_no_temp_files(isolated_data_dir):
    persistence.log_mistake(persistence.make_mistake_entry("i", "c", "q", "a", "b"))
    persistence.log_confidence("i", "c", 3, True)
    persistence.set_confidence_prompt_enabled(False)
    # Three kinds of sidecar, and no ".tmp" left anywhere:
    #   .lock         empty, flock()ed for the length of a read-modify-write on
    #                 the shared journals, so a second app running at the same
    #                 time cannot clobber rows we just wrote;
    #   .schema.json  the version marker (a sidecar, never a key in the data —
    #                 coach.py and dashboard.py require a plain JSON list).
    assert sorted(p.name for p in isolated_data_dir.iterdir()) == [
        "confidence.json", "confidence.json.lock", "confidence.json.schema.json",
        "mistakes.json", "mistakes.json.lock", "mistakes.json.schema.json",
        "qec_settings.json", "qec_settings.json.schema.json"]
    assert (isolated_data_dir / "mistakes.json.lock").read_bytes() == b""


# ── Schema versioning, migration and backups ──────────────────────────────────

@pytest.mark.parametrize("name,kind", [
    ("mistakes.json", "mistakes"), ("confidence.json", "confidence"),
    ("qec_flagged.json", "flagged"), ("qec_history.json", "history"),
    ("qec_settings.json", "settings"),
])
def test_every_file_this_app_writes_is_version_stamped(isolated_data_dir, name, kind):
    persistence.log_mistake(persistence.make_mistake_entry("i", "c", "q", "a", "b"))
    persistence.log_confidence("i", "c", 3, True)
    persistence.toggle_flag("i", "a question", "c")
    persistence.save_session(_one_session())
    persistence.set_confidence_prompt_enabled(False)

    meta = json.loads((isolated_data_dir / f"{name}.schema.json").read_text())
    assert meta["file"] == name
    assert meta["kind"] == kind
    assert meta["schema"] == schema.get(kind).version == 1
    assert meta["written_by"].startswith("common/")
    assert isinstance(meta["updated"], float)
    # …and the data file itself is still exactly the shape it always was.
    assert isinstance(json.loads((isolated_data_dir / name).read_text()), list) \
        or name == "qec_settings.json"


def test_an_unmarked_file_is_read_as_v1_and_stamped_on_the_next_write(isolated_data_dir):
    """Every file written before versioning existed is a v1 file."""
    isolated_data_dir.mkdir(parents=True, exist_ok=True)
    legacy = [persistence.make_mistake_entry("old", "c", "q", "a", "b",
                                             timestamp=1.0)]
    (isolated_data_dir / "mistakes.json").write_text(json.dumps(legacy))
    assert not (isolated_data_dir / "mistakes.json.schema.json").exists()

    assert [r["id"] for r in persistence.load_mistakes()] == ["old"]
    persistence.log_mistake(persistence.make_mistake_entry("new", "c", "q", "a", "b"))
    assert [r["id"] for r in persistence.load_mistakes()] == ["old", "new"]
    assert json.loads(
        (isolated_data_dir / "mistakes.json.schema.json").read_text())["schema"] == 1


def test_a_newer_file_is_refused_rather_than_overwritten(isolated_data_dir):
    """A build that does not understand v99 must not write its v1 view over it."""
    persistence.log_mistake(persistence.make_mistake_entry("mine", "c", "q", "a", "b"))
    side = isolated_data_dir / "mistakes.json.schema.json"
    side.write_text(json.dumps({"file": "mistakes.json", "kind": "mistakes",
                                "schema": 99}))
    before = (isolated_data_dir / "mistakes.json").read_text()

    persistence.clear_write_error()
    persistence.log_mistake(persistence.make_mistake_entry("later", "c", "q", "a", "b"))

    assert (isolated_data_dir / "mistakes.json").read_text() == before   # untouched
    err = persistence.last_write_error()
    assert isinstance(err, schema.SchemaTooNewError)
    assert err.found == 99 and err.understood == 1
    persistence.clear_write_error()
    assert persistence.last_write_error() is None


def test_a_migration_runs_forward_in_memory_without_rewriting_the_file(isolated_data_dir):
    """Reading an old file is never destructive; the write is what upgrades it."""
    isolated_data_dir.mkdir(parents=True, exist_ok=True)
    (isolated_data_dir / "qec_settings.json").write_text(
        json.dumps({"confidence_prompt": False}))
    (isolated_data_dir / "qec_settings.json.schema.json").write_text(
        json.dumps({"file": "qec_settings.json", "kind": "settings", "schema": 1}))

    original = schema.get("settings")
    schema.register(schema.FileSchema(
        "settings", version=2,
        migrations={1: lambda d: {**d, "migrated": True}}), replace=True)
    try:
        assert persistence.load_settings()["migrated"] is True
        assert "migrated" not in json.loads(          # the file is untouched
            (isolated_data_dir / "qec_settings.json").read_text())
        persistence.set_confidence_prompt_enabled(True)
        on_disk = json.loads((isolated_data_dir / "qec_settings.json").read_text())
        assert on_disk == {"confidence_prompt": True, "migrated": True}
        assert json.loads(
            (isolated_data_dir / "qec_settings.json.schema.json").read_text()
        )["schema"] == 2
    finally:
        schema.register(original, replace=True)


def test_the_first_write_of_a_session_rotates_a_backup(isolated_data_dir):
    """One backup per file per session, three generations deep."""
    target = isolated_data_dir / "mistakes.json"
    persistence.log_mistake(persistence.make_mistake_entry("gen0", "c", "q", "a", "b"))
    assert not target.with_suffix(".json.bak").exists()   # nothing to back up yet

    for generation in range(1, 4):
        schema.reset_session()                            # a new "session"
        persistence.log_mistake(persistence.make_mistake_entry(
            f"gen{generation}", "c", "q", "a", "b"))
        # a second write in the same session does not make a second backup
        persistence.log_mistake(persistence.make_mistake_entry(
            f"gen{generation}b", "c", "q", "a", "b"))

    def ids(path):
        return [r["id"] for r in json.loads(path.read_text())]

    assert ids(target)[-1] == "gen3b"
    assert ids(isolated_data_dir / "mistakes.json.bak") == [
        "gen0", "gen1", "gen1b", "gen2", "gen2b"]
    assert ids(isolated_data_dir / "mistakes.json.bak.1") == ["gen0", "gen1", "gen1b"]
    assert ids(isolated_data_dir / "mistakes.json.bak.2") == ["gen0"]
    assert not (isolated_data_dir / "mistakes.json.bak.3").exists()

    assert schema.restore_backup(target, 2) is True
    assert ids(target) == ["gen0"]


# ── Settings opt-out ──────────────────────────────────────────────────────────

def test_confidence_prompt_opt_out_round_trip(isolated_data_dir):
    assert persistence.confidence_prompt_enabled() is True
    persistence.set_confidence_prompt_enabled(False)
    assert persistence.confidence_prompt_enabled() is False
    assert json.loads((isolated_data_dir / "qec_settings.json").read_text()) == {
        "confidence_prompt": False}
    persistence.set_confidence_prompt_enabled(True)
    assert persistence.confidence_prompt_enabled() is True


def test_settings_file_keeps_unknown_keys():
    persistence.save_settings({"confidence_prompt": False, "future_key": 7})
    assert persistence.load_settings() == {"confidence_prompt": False, "future_key": 7}
    persistence.set_confidence_prompt_enabled(True)
    assert persistence.load_settings() == {"confidence_prompt": True, "future_key": 7}


# ── The new files must not disturb the load-bearing history schema ────────────

def test_history_and_flag_schemas_are_untouched(isolated_data_dir):
    p = Problem(id="p1", category="Surface Code", difficulty="beginner", question="q",
                choices=["a", "b"], correct_index=0, grade_mode=GradeMode.AUTO)
    from core.models import SessionStats
    stats = SessionStats(total=1, correct=0,
                         attempts=[Attempt(p, "B", 0, Verdict.INCORRECT, "fb")])
    persistence.save_session(stats)
    persistence.toggle_flag("p1", "q", "Surface Code")
    persistence.log_mistake(persistence.make_mistake_entry("p1", "Surface Code", "q", "B", "A. a"))

    sessions = json.loads((isolated_data_dir / "qec_history.json").read_text())
    assert set(sessions[0]) == {"total", "correct", "accuracy", "timestamp", "attempts"}
    assert set(sessions[0]["attempts"][0]) == {
        "problem_id", "category", "difficulty", "score", "verdict",
        "hints_used", "elapsed_secs"}
    # qec_flagged.json used to be a bare id list written with a plain
    # write_text (truncate first: a crash mid-write lost every flag).  It is
    # now the suite's contract shape, written atomically; coach.py parses both,
    # and the label means the review queue shows the question, not the id.
    flagged = json.loads((isolated_data_dir / "qec_flagged.json").read_text())
    assert flagged == [{"id": "p1", "label": "q", "category": "Surface Code",
                        "app": "qec-trainer", "timestamp": flagged[0]["timestamp"]}]
    assert persistence.load_flagged() == {"p1"}


# ---------------------------------------------------------------------------
# Shared-file contract: another app's rows are never ours to rewrite
# ---------------------------------------------------------------------------

FOREIGN_MISTAKE_ROW = {
    "id": "tutor-7", "app": "quantum-tutor", "category": "Gates",
    "question": "q", "your_answer": "a", "correct_answer": "b",
    "cause": "confused", "note": "n", "timestamp": 1.0, "resolved": False,
    "revision": 3,                       # keys this app's schema knows nothing
    "tags": ["endianness", {"deep": True}],   # about: they must survive anyway
}
FOREIGN_CONFIDENCE_ROW = {
    "id": "tutor-7", "app": "quantum-tutor", "category": "Gates",
    "confidence": 2, "correct": True, "timestamp": 1.0,
    "source": "tutor-v2", "latency_ms": 940,
}


def test_a_foreign_row_keeps_its_unknown_keys_through_our_writes(isolated_data_dir):
    """Another app's rows come back byte for byte — extra keys included.

    Both files are shared, so a rewrite here must put every row this app does
    not own back exactly as it was read.  Normalising a foreign row through
    this app's schema would silently drop whatever the owning app added to it.
    """
    isolated_data_dir.mkdir(parents=True, exist_ok=True)
    (isolated_data_dir / "mistakes.json").write_text(json.dumps([FOREIGN_MISTAKE_ROW]))
    (isolated_data_dir / "confidence.json").write_text(json.dumps([FOREIGN_CONFIDENCE_ROW]))

    persistence.log_mistake(persistence.make_mistake_entry(
        "ours", "Stabilisers", "q", "a", "b"))
    persistence.set_mistake_cause("ours", "misread")
    persistence.resolve_mistake("ours")
    persistence.log_confidence("ours", "Stabilisers", 3, False)

    mistakes = json.loads((isolated_data_dir / "mistakes.json").read_text())
    assert mistakes[0] == FOREIGN_MISTAKE_ROW      # unchanged, unknown keys intact
    assert len(mistakes) > 1                       # and our own row was written
    assert {r["app"] for r in mistakes[1:]} == {"qec-trainer"}
    confidence = json.loads((isolated_data_dir / "confidence.json").read_text())
    assert confidence[0] == FOREIGN_CONFIDENCE_ROW
    assert len(confidence) > 1
    assert {r["app"] for r in confidence[1:]} == {"qec-trainer"}
