"""Mistake journal, confidence calibration and app settings — pure helpers, no Qt."""
from __future__ import annotations

import json
import time

import pytest

import persistence
from core.models import Attempt, GradeMode, Problem, Verdict, answer_texts

MISTAKE_KEYS = {"id", "app", "category", "question", "your_answer",
                "correct_answer", "cause", "note", "timestamp", "resolved"}
CONFIDENCE_KEYS = {"id", "app", "category", "confidence", "correct", "timestamp"}


# --------------------------------------------------------------------- schema
def test_make_mistake_entry_matches_the_shared_contract():
    e = persistence.make_mistake_entry(
        "qaoa_structure", "QAOA", "Which layer comes first?", "B. mixer",
        "A. cost", cause="knew_but_slipped", note="U_C before U_B", timestamp=123.5)
    assert set(e) == MISTAKE_KEYS
    assert e == {
        "id": "qaoa_structure", "app": "vqa-trainer", "category": "QAOA",
        "question": "Which layer comes first?", "your_answer": "B. mixer",
        "correct_answer": "A. cost", "cause": "knew_but_slipped",
        "note": "U_C before U_B", "timestamp": 123.5, "resolved": False,
    }
    assert isinstance(e["timestamp"], float) and isinstance(e["resolved"], bool)


def test_entry_fields_are_clipped_to_200_chars_and_causes_validated():
    e = persistence.make_mistake_entry("p", "QAOA", "q" * 500, "a" * 500, "c" * 500,
                                       cause="NOT A CAUSE", note="n" * 500)
    for field in ("question", "your_answer", "correct_answer", "note"):
        assert len(e[field]) == 200, field
        assert e[field].endswith("…")
    assert e["cause"] is None, "an unknown cause degrades to null, never crashes"
    assert persistence.normalise_cause(None) is None
    for cause in persistence.MISTAKE_CAUSES:
        assert persistence.normalise_cause(cause.upper()) == cause
    assert set(persistence.MISTAKE_CAUSES) == {
        "misread", "didnt_know", "knew_but_slipped", "confused", "out_of_time", "other"}
    assert set(persistence.CAUSE_LABELS) == set(persistence.MISTAKE_CAUSES)


def test_make_confidence_entry_matches_the_shared_contract():
    e = persistence.make_confidence_entry("bp_definition", "Barren Plateaus", 4, False,
                                          timestamp=99.0)
    assert e == {"id": "bp_definition", "app": "vqa-trainer",
                 "category": "Barren Plateaus", "confidence": 4,
                 "correct": False, "timestamp": 99.0}
    assert set(e) == CONFIDENCE_KEYS
    assert persistence.make_confidence_entry("p", "C", 9, True)["confidence"] == 4
    assert persistence.make_confidence_entry("p", "C", 0, True)["confidence"] == 1
    assert persistence.make_confidence_entry("p", "C", "junk", True)["confidence"] == 1


# ------------------------------------------------------------------ round trip
def test_log_mistake_writes_json_and_keeps_repeats(isolated_data_dir):
    assert persistence.load_mistakes() == []
    persistence.log_mistake("ps_rule", "Parameter Shift", "q", "wrong", "right")
    persistence.log_mistake("ps_rule", "Parameter Shift", "q", "wrong again", "right")
    rows = json.loads(persistence.MISTAKES_FILE.read_text())
    assert rows == persistence.load_mistakes() and len(rows) == 2
    assert [r["cause"] for r in rows] == [None, None], "skipping still logs the mistake"
    assert abs(rows[0]["timestamp"] - time.time()) < 60
    assert persistence.MISTAKES_FILE.parent == isolated_data_dir


def test_cause_updates_the_latest_row_and_note_survives():
    persistence.log_mistake("vqe_uccsd", "VQE Fundamentals", "q", "A", "B", timestamp=1.0)
    persistence.log_mistake("vqe_uccsd", "VQE Fundamentals", "q", "C", "B", timestamp=2.0)
    updated = persistence.set_mistake_cause("vqe_uccsd", "misread", "read the wrong ansatz")
    assert updated["timestamp"] == 2.0
    rows = persistence.load_mistakes()
    assert [r["cause"] for r in rows] == [None, "misread"]
    assert rows[1]["note"] == "read the wrong ansatz"
    # a note-only edit keeps the cause
    persistence.set_mistake_cause("vqe_uccsd", "misread", "shorter note")
    assert persistence.load_mistakes()[1] == dict(rows[1], note="shorter note")
    assert persistence.set_mistake_cause("never_seen", "other") is None


def test_answering_correctly_later_resolves_every_matching_row():
    persistence.log_mistake("qaoa_mixer_role", "QAOA", "q", "A", "B")
    persistence.log_mistake("qaoa_mixer_role", "QAOA", "q", "C", "B")
    persistence.log_mistake("other_item", "QAOA", "q", "A", "B")
    assert persistence.resolve_mistakes("qaoa_mixer_role") == 2
    assert persistence.resolve_mistakes("qaoa_mixer_role") == 0, "idempotent"
    by_id = {}
    for r in persistence.load_mistakes():
        by_id.setdefault(r["id"], []).append(r["resolved"])
    assert by_id == {"qaoa_mixer_role": [True, True], "other_item": [False]}


def test_rows_from_other_apps_are_left_alone():
    persistence.log_mistake("shared_id", "QAOA", "q", "A", "B", app="qec-trainer")
    persistence.log_mistake("shared_id", "QAOA", "q", "A", "B")
    assert persistence.resolve_mistakes("shared_id") == 1
    assert persistence.set_mistake_cause("shared_id", "confused")["app"] == "vqa-trainer"
    foreign = [r for r in persistence.load_mistakes() if r["app"] == "qec-trainer"][0]
    assert foreign["resolved"] is False and foreign["cause"] is None


def test_cause_counts_are_the_payload():
    for cause in ("misread", "misread", "didnt_know", None):
        persistence.log_mistake(f"p{cause}{id(cause)}", "QAOA", "q", "A", "B", cause=cause)
    persistence.log_mistake("x", "QAOA", "q", "A", "B", cause="misread", app="math-quiz")
    assert persistence.mistake_cause_counts() == {"misread": 2, "didnt_know": 1, "": 1}
    assert persistence.mistake_cause_counts(app="")["misread"] == 3
    persistence.resolve_mistakes("pdidnt_know" + str(id("didnt_know")))
    assert persistence.mistake_cause_counts(unresolved_only=True)["misread"] == 2


def test_confidence_round_trip_and_breakdown(isolated_data_dir):
    persistence.log_confidence("a", "QAOA", 4, False)
    persistence.log_confidence("b", "QAOA", 4, True)
    persistence.log_confidence("c", "QAOA", 1, False)
    persistence.log_confidence("d", "QAOA", 4, True, app="exam-sim")
    rows = json.loads(persistence.CONFIDENCE_FILE.read_text())
    assert rows == persistence.load_confidence() and len(rows) == 4
    assert all(set(r) == CONFIDENCE_KEYS for r in rows)
    # confidently wrong shows up as a poor ratio at level 4
    assert persistence.confidence_breakdown() == {1: (0, 1), 4: (1, 2)}
    assert persistence.confidence_breakdown(app="")[4] == (2, 3)


# ------------------------------------------------------------------ robustness
@pytest.mark.parametrize("junk", ['{"not": "a list"}', "not json at all", "", "[1, 2, 3]"])
def test_corrupt_files_start_fresh_and_never_crash(isolated_data_dir, junk):
    isolated_data_dir.mkdir(parents=True, exist_ok=True)
    persistence.MISTAKES_FILE.write_text(junk)
    persistence.CONFIDENCE_FILE.write_text(junk)
    persistence.SETTINGS_FILE.write_text(junk)
    assert persistence.load_mistakes() == []
    assert persistence.load_confidence() == []
    assert persistence.confidence_prompt_enabled() is True
    persistence.log_mistake("p", "QAOA", "q", "A", "B")
    persistence.log_confidence("p", "QAOA", 2, False)
    assert len(persistence.load_mistakes()) == 1
    assert len(persistence.load_confidence()) == 1


def test_missing_files_read_as_empty(isolated_data_dir):
    assert not isolated_data_dir.exists()
    assert persistence.load_mistakes() == [] and persistence.load_confidence() == []
    assert persistence.load_settings() == {"confidence_prompt": True}
    assert not isolated_data_dir.exists(), "reading must not create the directory"


def test_writes_are_atomic_and_leave_no_temp_files(isolated_data_dir):
    persistence.log_mistake("p", "QAOA", "q", "A", "B")
    persistence.log_confidence("p", "QAOA", 3, False)
    persistence.set_confidence_prompt_enabled(False)
    # The ".lock" sidecars are journal_sync's: empty files flock()ed for the
    # length of a read-modify-write on the shared journals, so another app
    # writing at the same moment cannot drop the rows we just appended.
    names = sorted(f.name for f in isolated_data_dir.iterdir())
    assert names == ["confidence.json", "confidence.json.lock",
                     "mistakes.json", "mistakes.json.lock", "vqa_settings.json"]
    assert (isolated_data_dir / "mistakes.json.lock").read_bytes() == b""


def test_growth_is_capped_at_the_newest_rows(monkeypatch):
    monkeypatch.setattr(persistence, "MAX_MISTAKES", 5)
    monkeypatch.setattr(persistence, "MAX_CONFIDENCE", 5)
    for i in range(12):
        persistence.log_mistake(f"p{i}", "QAOA", "q", "A", "B", timestamp=float(i))
        persistence.log_confidence(f"p{i}", "QAOA", 2, False, timestamp=float(i))
    assert [r["id"] for r in persistence.load_mistakes()] == [f"p{i}" for i in range(7, 12)]
    assert [r["id"] for r in persistence.load_confidence()] == [f"p{i}" for i in range(7, 12)]


def test_settings_opt_out_round_trip(isolated_data_dir):
    assert persistence.confidence_prompt_enabled() is True
    persistence.set_confidence_prompt_enabled(False)
    assert json.loads(persistence.SETTINGS_FILE.read_text()) == {"confidence_prompt": False}
    assert persistence.confidence_prompt_enabled() is False
    persistence.set_confidence_prompt_enabled(True)
    assert persistence.confidence_prompt_enabled() is True


def test_settings_keep_unknown_keys_written_by_a_later_version():
    persistence.save_settings({"confidence_prompt": False, "future_flag": 7})
    assert persistence.load_settings() == {"confidence_prompt": False, "future_flag": 7}
    persistence.set_confidence_prompt_enabled(True)
    assert persistence.load_settings()["future_flag"] == 7


# ------------------------------------------------------- answer display helper
def test_answer_texts_expands_letters_into_choice_text():
    p = Problem(id="t", category="QAOA", difficulty="beginner", question="q?",
                choices=["cost layer", "mixer layer", "c", "d"], correct_index=0,
                explanation="because", grade_mode=GradeMode.MC)
    given, correct = answer_texts(Attempt(p, "B", 0, Verdict.INCORRECT, "fb"))
    assert given == "B. mixer layer" and correct == "A. cost layer"
    blank, _ = answer_texts(Attempt(p, "", 0, Verdict.INCORRECT, "fb"))
    assert blank == "(no answer)"

    n = Problem(id="n", category="Parameter Shift", difficulty="advanced", question="q",
                correct_value=-0.8660254, tolerance=1e-3, explanation="shift",
                grade_mode=GradeMode.AUTO)
    given, correct = answer_texts(Attempt(n, "0.5", 0, Verdict.INCORRECT, "fb"))
    assert given == "0.5" and correct == "-0.866"

    f = Problem(id="f", category="VQE Fundamentals", difficulty="advanced",
                question="explain", explanation="model answer text",
                grade_mode=GradeMode.CLAUDE)
    given, correct = answer_texts(Attempt(f, "my essay", 3, Verdict.PARTIAL, "fb",
                                          model_answer="the reference answer"))
    assert given == "my essay" and correct == "the reference answer"
    _, fallback = answer_texts(Attempt(f, "my essay", 3, Verdict.PARTIAL, "fb"))
    assert fallback == "model answer text"


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

    persistence.log_mistake("ours", "QAOA", "q", "A", "B")
    persistence.set_mistake_cause("ours", "misread")
    persistence.resolve_mistakes("ours")
    persistence.log_confidence("ours", "QAOA", 3, False)

    mistakes = json.loads((isolated_data_dir / "mistakes.json").read_text())
    assert mistakes[0] == FOREIGN_MISTAKE_ROW      # unchanged, unknown keys intact
    assert len(mistakes) > 1                       # and our own row was written
    assert {r["app"] for r in mistakes[1:]} == {"vqa-trainer"}
    confidence = json.loads((isolated_data_dir / "confidence.json").read_text())
    assert confidence[0] == FOREIGN_CONFIDENCE_ROW
    assert len(confidence) > 1
    assert {r["app"] for r in confidence[1:]} == {"vqa-trainer"}
