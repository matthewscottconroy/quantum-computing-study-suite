"""Mistake journal + confidence calibration contract: file schemas, cause
categorisation, resolution, atomic writes, caps, corrupt-file tolerance and the
QUANTUM_STUDY_DATA_DIR override. No Qt here — all helpers are pure/­file-level."""
from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys
import time

import pytest

import persistence
from core.models import AnswerFormat, Attempt, Problem, ProblemCategory

MISTAKE_FIELDS = {
    "id", "app", "category", "question", "your_answer", "correct_answer",
    "cause", "note", "timestamp", "resolved",
}
CONFIDENCE_FIELDS = {"id", "app", "category", "confidence", "correct", "timestamp"}


def _problem(text: str = "Apply H to |0⟩. What is the output state?",
             cat: ProblemCategory = ProblemCategory.SINGLE_GATE_OUTPUT,
             fmt: AnswerFormat = AnswerFormat.MULTIPLE_CHOICE,
             pid: str | None = None) -> Problem:
    return Problem(
        category=cat, difficulty="beginner", question_text=text,
        answer_format=fmt, correct_answer="1",
        choices=["|0⟩", "|+⟩", "|1⟩", "|−⟩"], circuit_png=None,
        aux_circuit_png=None, matrix_str=None, state_str=None,
        solution_steps=["H|0⟩ = |+⟩"], key_concepts=["Hadamard"], problem_id=pid,
    )


# ── Entry construction (pure) ─────────────────────────────────────────────────

def test_make_mistake_entry_matches_the_shared_schema():
    p = _problem()
    entry = persistence.make_mistake_entry(p, "|1⟩", "|+⟩", cause="misread",
                                           note="little-endian again")
    assert set(entry) == MISTAKE_FIELDS
    assert entry["id"] == persistence.flag_id_for(p)
    assert entry["app"] == "circuit-trainer"
    assert entry["category"] == ProblemCategory.SINGLE_GATE_OUTPUT.value
    assert entry["question"] == "Apply H to |0⟩. What is the output state?"
    assert entry["your_answer"] == "|1⟩" and entry["correct_answer"] == "|+⟩"
    assert entry["cause"] == "misread"
    assert entry["note"] == "little-endian again"
    assert isinstance(entry["timestamp"], float)
    assert abs(time.time() - entry["timestamp"]) < 60
    assert entry["resolved"] is False


def test_mistake_entry_clips_long_text_and_normalises_whitespace():
    p = _problem("word  " * 200 + "\n\ntail")
    entry = persistence.make_mistake_entry(p, "y" * 500, "c" * 500)
    for field in ("question", "your_answer", "correct_answer"):
        assert len(entry[field]) <= 200, field
    assert entry["question"].endswith("…") and "  " not in entry["question"]
    assert persistence.clip_field("  a   b\tc  ") == "a b c"


def test_unknown_cause_is_stored_as_none():
    p = _problem()
    assert persistence.make_mistake_entry(p, "a", "b", cause="banana")["cause"] is None
    assert persistence.make_mistake_entry(p, "a", "b")["cause"] is None
    assert persistence.normalise_cause("didnt_know") == "didnt_know"
    assert persistence.MISTAKE_CAUSES == (
        "misread", "didnt_know", "knew_but_slipped", "confused",
        "out_of_time", "other")


def test_answer_texts_resolve_choice_labels_and_free_form():
    p = _problem()
    yours, correct = persistence.answer_texts_for(
        Attempt(p, "2", False, 0, "fb"))
    assert (yours, correct) == ("|1⟩", "|+⟩")
    # No answer at all (sprint timeout) still produces readable text.
    assert persistence.answer_texts_for(Attempt(p, "", False, 0, "fb"))[0] == "(no answer)"

    ff = _problem("Explain the circuit.", fmt=AnswerFormat.FREE_FORM)
    ff.choices = None
    yours, correct = persistence.answer_texts_for(
        Attempt(ff, "it entangles", False, 2, "fb", model_answer="It makes a Bell state"))
    assert yours == "it entangles" and correct == "It makes a Bell state"
    # No model answer -> the worked solution is the reference.
    assert persistence.answer_texts_for(
        Attempt(ff, "x", False, 0, "fb"))[1] == "H|0⟩ = |+⟩"


# ── File round-trip ───────────────────────────────────────────────────────────

def test_log_mistake_round_trips_through_the_data_dir(isolated_data_dir):
    assert persistence.load_mistakes() == []
    p = _problem()
    entry = persistence.log_mistake_for_attempt(Attempt(p, "0", False, 0, "fb"))

    path = isolated_data_dir / "mistakes.json"
    assert persistence.mistakes_file() == path and path.exists()
    stored = json.loads(path.read_text())
    assert stored == [entry] == persistence.load_mistakes()
    assert set(stored[0]) == MISTAKE_FIELDS
    assert stored[0]["cause"] is None and stored[0]["resolved"] is False
    assert stored[0]["your_answer"] == "|0⟩"
    # Same id as the flag contract, so journal and flags key identically.
    assert stored[0]["id"] == persistence.flag_id_for(p)


def test_choosing_a_cause_updates_the_same_entry(isolated_data_dir):
    p = _problem()
    persistence.log_mistake_for_attempt(Attempt(p, "0", False, 0, "fb"))
    updated = persistence.update_mistake(persistence.flag_id_for(p),
                                         cause="knew_but_slipped", note="sign error")
    assert updated["cause"] == "knew_but_slipped" and updated["note"] == "sign error"
    entries = persistence.load_mistakes()
    assert len(entries) == 1                      # updated, not appended
    assert entries[0]["cause"] == "knew_but_slipped"
    # A note-only update keeps the cause.
    persistence.update_mistake(persistence.flag_id_for(p), note="check endianness")
    only = persistence.load_mistakes()[0]
    assert only["cause"] == "knew_but_slipped" and only["note"] == "check endianness"
    assert persistence.update_mistake("no-such-id", cause="other") is None


def test_update_targets_the_most_recent_entry_for_that_item(isolated_data_dir):
    p = _problem()
    persistence.log_mistake_for_attempt(Attempt(p, "0", False, 0, "fb"))
    persistence.log_mistake_for_attempt(Attempt(p, "3", False, 0, "fb"))
    persistence.update_mistake(persistence.flag_id_for(p), cause="confused")
    first, second = persistence.load_mistakes()
    assert first["cause"] is None and second["cause"] == "confused"
    assert second["your_answer"] == "|−⟩"


def test_answering_correctly_later_resolves_the_entries(isolated_data_dir):
    p = _problem()
    other = _problem("A different question", ProblemCategory.NOISE_CHANNEL)
    persistence.log_mistake_for_attempt(Attempt(p, "0", False, 0, "fb"))
    persistence.log_mistake_for_attempt(Attempt(p, "2", False, 0, "fb"))
    persistence.log_mistake_for_attempt(Attempt(other, "0", False, 0, "fb"))

    assert persistence.resolve_mistake(persistence.flag_id_for(p)) == 2
    by_id = {}
    for e in persistence.load_mistakes():
        by_id.setdefault(e["id"], []).append(e["resolved"])
    assert by_id[persistence.flag_id_for(p)] == [True, True]
    assert by_id[persistence.flag_id_for(other)] == [False]
    # Idempotent: nothing left open to resolve.
    assert persistence.resolve_mistake(persistence.flag_id_for(p)) == 0


def test_cause_counts_summarise_the_journal(isolated_data_dir):
    p, q = _problem("one"), _problem("two")
    persistence.log_mistake_for_attempt(Attempt(p, "0", False, 0, "fb"))
    persistence.update_mistake(persistence.flag_id_for(p), cause="misread")
    persistence.log_mistake_for_attempt(Attempt(q, "0", False, 0, "fb"))
    assert persistence.mistake_cause_counts() == {"misread": 1, "": 1}
    persistence.resolve_mistake(persistence.flag_id_for(p))
    assert persistence.mistake_cause_counts(include_resolved=False) == {"": 1}


# ── Confidence ────────────────────────────────────────────────────────────────

def test_log_confidence_writes_the_pairing(isolated_data_dir):
    row = persistence.log_confidence("gs:H-X-H:0", "Gate sequence", 4, False)
    path = isolated_data_dir / "confidence.json"
    assert persistence.confidence_file() == path
    assert json.loads(path.read_text()) == [row]
    assert set(row) == CONFIDENCE_FIELDS
    assert row["id"] == "gs:H-X-H:0" and row["app"] == "circuit-trainer"
    assert row["category"] == "Gate sequence"
    assert row["confidence"] == 4 and row["correct"] is False
    assert abs(time.time() - row["timestamp"]) < 60


@pytest.mark.parametrize("bad", [None, 0, 5, -1, "high", "3", 2.7, True])
def test_bad_or_missing_confidence_records_nothing(isolated_data_dir, bad):
    assert persistence.log_confidence("id", "cat", bad, True) is None
    assert persistence.load_confidence() == []
    assert not (isolated_data_dir / "confidence.json").exists()


def test_make_confidence_entry_rejects_out_of_range():
    with pytest.raises(ValueError):
        persistence.make_confidence_entry("id", "cat", 7, True)
    assert persistence.CONFIDENCE_LEVELS == (1, 2, 3, 4)


def test_calibration_finds_confidently_wrong(isolated_data_dir):
    for conf, ok in [(4, False), (4, False), (4, True), (1, True), (2, False)]:
        persistence.log_confidence("i", "Noise channel", conf, ok)
    assert persistence.calibration_by_level() == {4: (1, 3), 1: (1, 1), 2: (0, 1)}


# ── Robustness: corrupt files, atomic writes, caps ────────────────────────────

@pytest.mark.parametrize("name", ["mistakes.json", "confidence.json", "trainer_prefs.json"])
def test_corrupt_files_are_treated_as_empty_and_recoverable(isolated_data_dir, name):
    isolated_data_dir.mkdir(parents=True, exist_ok=True)
    path = isolated_data_dir / name
    for junk in ("{not json", json.dumps("a string"), json.dumps({"k": "v"}), ""):
        path.write_text(junk)
        assert persistence.load_mistakes() == [] or name != "mistakes.json"
        assert persistence.load_confidence() == [] or name != "confidence.json"
        assert persistence.confidence_prompt_enabled() in (True, False)

    path.write_text("{not json")
    persistence.log_mistake_for_attempt(Attempt(_problem(), "0", False, 0, "fb"))
    persistence.log_confidence("i", "c", 3, True)
    persistence.set_confidence_prompt_enabled(False)
    assert len(persistence.load_mistakes()) == 1
    assert len(persistence.load_confidence()) == 1
    assert persistence.confidence_prompt_enabled() is False


def test_malformed_rows_are_skipped(isolated_data_dir):
    isolated_data_dir.mkdir(parents=True, exist_ok=True)
    (isolated_data_dir / "mistakes.json").write_text(
        json.dumps(["bare", 3, {"no_id": 1}, {"id": "keep", "cause": None}]))
    assert [e["id"] for e in persistence.load_mistakes()] == ["keep"]
    (isolated_data_dir / "confidence.json").write_text(
        json.dumps([{"no_id": 1}, {"id": "keep", "confidence": 2}]))
    assert [e["id"] for e in persistence.load_confidence()] == ["keep"]


def test_writes_are_atomic_and_leave_no_temp_files(isolated_data_dir):
    persistence.log_mistake_for_attempt(Attempt(_problem(), "0", False, 0, "fb"))
    persistence.log_confidence("i", "c", 2, True)
    persistence.set_confidence_prompt_enabled(True)
    leftovers = [p.name for p in isolated_data_dir.iterdir() if p.suffix == ".tmp"]
    assert leftovers == []
    # The ".lock" sidecars belong to journal_sync: empty files flock()ed for the
    # length of each read-modify-write so a second app cannot clobber rows we
    # just appended to the shared journals.
    assert sorted(p.name for p in isolated_data_dir.iterdir()) == [
        "confidence.json", "confidence.json.lock",
        "mistakes.json", "mistakes.json.lock", "trainer_prefs.json"]
    assert (isolated_data_dir / "mistakes.json.lock").read_bytes() == b""


def test_files_are_capped_at_the_documented_maximums(isolated_data_dir, monkeypatch):
    monkeypatch.setattr(persistence, "_MAX_MISTAKES", 3)
    monkeypatch.setattr(persistence, "_MAX_CONFIDENCE", 3)
    for i in range(6):
        persistence.append_mistake(
            persistence.make_mistake_entry(_problem(f"q{i}"), str(i), "c"))
        persistence.log_confidence(f"i{i}", "c", 1, True)
    assert [e["your_answer"] for e in persistence.load_mistakes()] == ["3", "4", "5"]
    assert [e["id"] for e in persistence.load_confidence()] == ["i3", "i4", "i5"]


def test_confidence_prompt_pref_round_trips(isolated_data_dir):
    assert persistence.confidence_prompt_enabled() is True      # default on
    persistence.set_confidence_prompt_enabled(False)
    assert persistence.prefs_file() == isolated_data_dir / "trainer_prefs.json"
    assert json.loads(persistence.prefs_file().read_text()) == {"confidence_prompt": False}
    assert persistence.confidence_prompt_enabled() is False
    persistence.set_confidence_prompt_enabled(True)
    assert persistence.confidence_prompt_enabled() is True
    # Unrelated keys survive.
    persistence.save_prefs({**persistence.load_prefs(), "other": 1})
    persistence.set_confidence_prompt_enabled(False)
    assert persistence.load_prefs() == {"confidence_prompt": False, "other": 1}


def test_existing_history_and_flag_files_are_untouched(isolated_data_dir):
    """The new files must not disturb the load-bearing schemas."""
    p = _problem()
    persistence.toggle_flag(p)
    persistence.log_mistake_for_attempt(Attempt(p, "0", False, 0, "fb"))
    flagged = json.loads((isolated_data_dir / "trainer_flagged.json").read_text())
    assert set(flagged[0]) == {"id", "label", "category", "app", "timestamp"}
    assert not (isolated_data_dir / "trainer_history.json").exists()


# ── QUANTUM_STUDY_DATA_DIR (read at import time — use a fresh interpreter) ────

_APP_ROOT = pathlib.Path(persistence.__file__).resolve().parent
_PRINT_PATHS = (
    "import json, persistence; print(json.dumps([str(persistence.mistakes_file()), "
    "str(persistence.confidence_file()), str(persistence.prefs_file())]))"
)


def _paths_in_fresh_interpreter(env: dict) -> list[str]:
    out = subprocess.run([sys.executable, "-c", _PRINT_PATHS], cwd=_APP_ROOT, env=env,
                         capture_output=True, text=True, check=True, timeout=120).stdout
    return json.loads(out)


def test_env_var_redirects_the_new_files(tmp_path):
    target = tmp_path / "redirected"
    env = {**os.environ, "QUANTUM_STUDY_DATA_DIR": str(target)}
    mistakes, confidence, prefs = _paths_in_fresh_interpreter(env)
    assert mistakes == str(target / "mistakes.json")
    assert confidence == str(target / "confidence.json")
    assert prefs == str(target / "trainer_prefs.json")


def test_default_location_when_env_var_unset():
    env = {k: v for k, v in os.environ.items() if k != "QUANTUM_STUDY_DATA_DIR"}
    mistakes, confidence, prefs = _paths_in_fresh_interpreter(env)
    expected = pathlib.Path.home() / ".local" / "share" / "quantum-study"
    assert mistakes == str(expected / "mistakes.json")
    assert confidence == str(expected / "confidence.json")
    assert prefs == str(expected / "trainer_prefs.json")


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

    attempt = Attempt(_problem(pid="ours"), "0", False, 0, "fb")
    entry = persistence.log_mistake_for_attempt(attempt)
    persistence.update_mistake(entry["id"], cause="misread")
    persistence.resolve_mistake(entry["id"])
    persistence.log_confidence(entry["id"], "Gates", 3, False)

    mistakes = json.loads((isolated_data_dir / "mistakes.json").read_text())
    assert mistakes[0] == FOREIGN_MISTAKE_ROW      # unchanged, unknown keys intact
    assert len(mistakes) > 1                       # and our own row was written
    assert {r["app"] for r in mistakes[1:]} == {"circuit-trainer"}
    confidence = json.loads((isolated_data_dir / "confidence.json").read_text())
    assert confidence[0] == FOREIGN_CONFIDENCE_ROW
    assert len(confidence) > 1
    assert {r["app"] for r in confidence[1:]} == {"circuit-trainer"}
