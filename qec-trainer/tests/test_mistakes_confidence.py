"""Mistake journal + confidence calibration: schema, helpers and headless UI.

The two files are the suite-wide contract (``mistakes.json`` /
``confidence.json``), so the schema is asserted field-for-field against a temp
data dir rather than by shape alone.
"""
from __future__ import annotations

import json
import os
import time

import pytest

import persistence
from core.models import Attempt, GradeMode, Problem, Verdict

MISTAKE_FIELDS = {
    "id", "app", "category", "question", "your_answer", "correct_answer",
    "cause", "note", "timestamp", "resolved",
}
CONFIDENCE_FIELDS = {"id", "app", "category", "confidence", "correct", "timestamp"}


# ── config honours QUANTUM_STUDY_DATA_DIR ─────────────────────────────────────

def test_config_resolves_every_file_under_the_env_override(tmp_path):
    """config.py must read QUANTUM_STUDY_DATA_DIR (8 of 10 apps already did)."""
    import importlib
    import config

    target = tmp_path / "elsewhere"
    old = os.environ.get("QUANTUM_STUDY_DATA_DIR")
    os.environ["QUANTUM_STUDY_DATA_DIR"] = str(target)
    try:
        fresh = importlib.reload(config)
        assert fresh.DATA_DIR == target
        for attr in ("HISTORY_FILE", "FLAGGED_FILE", "MISTAKES_FILE",
                     "CONFIDENCE_FILE", "SETTINGS_FILE"):
            assert getattr(fresh, attr).parent == target, attr
        assert fresh.MISTAKES_FILE.name == "mistakes.json"
        assert fresh.CONFIDENCE_FILE.name == "confidence.json"
        # the API key lives in ~/.config and is deliberately not moved
        assert fresh.API_KEY_FILE.name == "api_key.txt"
    finally:
        if old is None:
            os.environ.pop("QUANTUM_STUDY_DATA_DIR", None)
        else:
            os.environ["QUANTUM_STUDY_DATA_DIR"] = old
        importlib.reload(config)


def test_config_default_is_unchanged_without_the_env_var(tmp_path):
    import importlib
    import pathlib
    import config

    old = os.environ.pop("QUANTUM_STUDY_DATA_DIR", None)
    try:
        fresh = importlib.reload(config)
        assert fresh.DATA_DIR == pathlib.Path.home() / ".local" / "share" / "quantum-study"
    finally:
        if old is not None:
            os.environ["QUANTUM_STUDY_DATA_DIR"] = old
        importlib.reload(config)


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


def test_relogging_an_open_mistake_updates_it_and_keeps_the_cause():
    persistence.log_mistake(persistence.make_mistake_entry("p", "C", "q", "A", "D"))
    persistence.set_mistake_cause("p", "misread", "slow down")
    persistence.log_mistake(persistence.make_mistake_entry("p", "C", "q", "B", "D"))
    rows = persistence.load_mistakes()
    assert len(rows) == 1
    assert rows[0]["your_answer"] == "B"          # refreshed
    assert rows[0]["cause"] == "misread"          # preserved
    assert rows[0]["note"] == "slow down"

    persistence.resolve_mistake("p")
    persistence.log_mistake(persistence.make_mistake_entry("p", "C", "q", "C", "D"))
    rows = persistence.load_mistakes()
    assert len(rows) == 2                         # a resolved item starts a new record
    assert rows[1]["cause"] is None


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
    assert persistence.calibration_summary() == {4: {"n": 3, "correct": 2},
                                                 1: {"n": 1, "correct": 1}}


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
    monkeypatch.setattr(persistence, "MISTAKES_MAX", 5)
    monkeypatch.setattr(persistence, "CONFIDENCE_MAX", 5)
    for i in range(12):
        persistence.log_mistake(persistence.make_mistake_entry(
            f"p{i}", "c", "q", "a", "b", timestamp=1000.0 + i))
        persistence.log_confidence(f"p{i}", "c", 3, True, timestamp=1000.0 + i)
    assert [r["id"] for r in persistence.load_mistakes()] == [f"p{i}" for i in range(7, 12)]
    assert [r["id"] for r in persistence.load_confidence()] == [f"p{i}" for i in range(7, 12)]


def test_writes_are_atomic_and_leave_no_temp_files(isolated_data_dir):
    persistence.log_mistake(persistence.make_mistake_entry("i", "c", "q", "a", "b"))
    persistence.log_confidence("i", "c", 3, True)
    persistence.set_confidence_prompt_enabled(False)
    # The ".lock" sidecars are journal_sync's: empty files flock()ed for the
    # length of a read-modify-write on the two shared journals, so a second app
    # running at the same time cannot clobber rows we just wrote.
    assert sorted(p.name for p in isolated_data_dir.iterdir()) == [
        "confidence.json", "confidence.json.lock",
        "mistakes.json", "mistakes.json.lock", "qec_settings.json"]
    assert (isolated_data_dir / "mistakes.json.lock").read_bytes() == b""


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
    persistence.toggle_flag("p1")
    persistence.log_mistake(persistence.make_mistake_entry("p1", "Surface Code", "q", "B", "A. a"))

    sessions = json.loads((isolated_data_dir / "qec_history.json").read_text())
    assert set(sessions[0]) == {"total", "correct", "accuracy", "timestamp", "attempts"}
    assert set(sessions[0]["attempts"][0]) == {
        "problem_id", "category", "difficulty", "score", "verdict",
        "hints_used", "elapsed_secs"}
    assert json.loads((isolated_data_dir / "qec_flagged.json").read_text()) == ["p1"]


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
