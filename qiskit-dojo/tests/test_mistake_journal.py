"""Mistake journal (mistakes.json) + confidence calibration (confidence.json).

Pure helpers first — schema field-for-field, cause taxonomy, upsert/resolve
semantics, foreign-app isolation, corruption tolerance, atomic writes and the
growth cap — then the dojo_settings.json opt-out.  Everything goes through the
``data_dir`` fixture, so the real ~/.local/share/quantum-study is never touched.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

import persistence

MISTAKE_KEYS = {"id", "app", "category", "question", "your_answer",
                "correct_answer", "cause", "note", "timestamp", "resolved"}
CONFIDENCE_KEYS = {"id", "app", "category", "confidence", "correct", "timestamp"}


def _mistakes(data_dir: Path) -> list[dict]:
    return json.loads((data_dir / "mistakes.json").read_text())


def _confidence(data_dir: Path) -> list[dict]:
    return json.loads((data_dir / "confidence.json").read_text())


def _entry(kid: str = "ra_little_endian", **kw) -> dict:
    base = dict(kata_id=kid, category="Results analysis",
                question="Per-qubit probabilities from counts",
                your_answer="FAILED: expected 0.5 for qubit 0, got 0.0",
                correct_answer="probs = [...]")
    base.update(kw)
    return persistence.make_mistake_entry(**base)


# ----------------------------------------------------------------- constants

def test_cause_taxonomy_is_the_agreed_one():
    assert persistence.MISTAKE_CAUSES == (
        "misread", "didnt_know", "knew_but_slipped", "confused",
        "out_of_time", "other",
    )
    assert set(persistence.CAUSE_LABELS) == set(persistence.MISTAKE_CAUSES)
    assert set(persistence.CONFIDENCE_LABELS) == {1, 2, 3, 4}


def test_paths_follow_the_shared_contract(data_dir):
    assert persistence.MISTAKES_FILE == data_dir / "mistakes.json"
    assert persistence.CONFIDENCE_FILE == data_dir / "confidence.json"
    assert persistence.SETTINGS_FILE == data_dir / "dojo_settings.json"


# ------------------------------------------------------------------ entries

def test_make_mistake_entry_is_pure_and_matches_the_schema(data_dir):
    before = time.time()
    e = _entry()
    assert not data_dir.exists()                      # pure: nothing written
    assert set(e) == MISTAKE_KEYS
    assert e["id"] == "ra_little_endian"
    assert e["app"] == "qiskit-dojo"
    assert e["category"] == "Results analysis"
    assert e["question"] == "Per-qubit probabilities from counts"
    assert e["your_answer"].startswith("FAILED:")
    assert e["cause"] is None
    assert e["note"] == ""
    assert isinstance(e["timestamp"], float) and e["timestamp"] >= before - 1
    assert e["resolved"] is False


def test_long_fields_are_clipped_to_200_chars_on_one_line():
    e = _entry(question="q " * 500, your_answer="line1\nline2",
               correct_answer="c" * 500, cause="other", note="n" * 500)
    for field in ("question", "your_answer", "correct_answer", "note"):
        assert len(e[field]) <= 200, field
    assert e["question"].endswith("…")
    assert e["your_answer"] == "line1 line2"          # newlines collapsed
    assert "\n" not in e["correct_answer"]


def test_unknown_cause_is_stored_as_none():
    assert _entry(cause="bogus")["cause"] is None
    assert _entry(cause=None)["cause"] is None
    assert _entry(cause="knew_but_slipped")["cause"] == "knew_but_slipped"


# --------------------------------------------------------------- log/resolve

def test_log_mistake_writes_the_file_and_reads_back(data_dir):
    persistence.log_mistake(_entry())
    on_disk = _mistakes(data_dir)
    assert len(on_disk) == 1
    assert set(on_disk[0]) == MISTAKE_KEYS
    assert persistence.load_mistakes() == on_disk
    assert persistence.mistakes_for_app() == on_disk
    assert persistence.mistakes_for_app("quantum-quiz") == []


def test_repeat_failures_fold_into_one_open_row(data_dir):
    persistence.log_mistake(_entry(your_answer="first try"))
    persistence.log_mistake(_entry(your_answer="second try"))
    rows = _mistakes(data_dir)
    assert len(rows) == 1
    assert rows[0]["your_answer"] == "second try"


def test_cause_and_note_survive_a_later_failure(data_dir):
    persistence.log_mistake(_entry())
    assert persistence.set_mistake_cause("ra_little_endian",
                                         "knew_but_slipped", "endianness again")
    persistence.log_mistake(_entry(your_answer="failed once more"))
    row = _mistakes(data_dir)[0]
    assert row["cause"] == "knew_but_slipped"
    assert row["note"] == "endianness again"
    assert row["your_answer"] == "failed once more"


def test_set_mistake_cause_can_clear_and_leaves_note_alone(data_dir):
    persistence.log_mistake(_entry())
    persistence.set_mistake_cause("ra_little_endian", "misread", "note A")
    persistence.set_mistake_cause("ra_little_endian", "bogus")   # -> None
    row = _mistakes(data_dir)[0]
    assert row["cause"] is None
    assert row["note"] == "note A"                    # note=None left it alone
    assert persistence.set_mistake_cause("never_seen", "misread") is False


def test_resolving_and_reopening(data_dir):
    persistence.log_mistake(_entry())
    assert persistence.resolve_mistakes("ra_little_endian") == 1
    assert _mistakes(data_dir)[0]["resolved"] is True
    assert persistence.resolve_mistakes("ra_little_endian") == 0   # idempotent

    persistence.log_mistake(_entry(your_answer="regressed"))       # new row
    rows = _mistakes(data_dir)
    assert [r["resolved"] for r in rows] == [True, False]
    assert rows[1]["your_answer"] == "regressed"


def test_other_apps_rows_are_never_touched(data_dir):
    data_dir.mkdir(parents=True)
    foreign = {"id": "ra_little_endian", "app": "quantum-quiz",
               "category": "Q", "question": "q", "your_answer": "a",
               "correct_answer": "b", "cause": "misread", "note": "",
               "timestamp": 1.0, "resolved": False}
    persistence.MISTAKES_FILE.write_text(json.dumps([foreign]))

    persistence.log_mistake(_entry())                 # same id, our app
    persistence.set_mistake_cause("ra_little_endian", "didnt_know")
    persistence.resolve_mistakes("ra_little_endian")

    rows = _mistakes(data_dir)
    assert rows[0] == foreign                         # byte-for-byte identical
    assert rows[1]["app"] == "qiskit-dojo" and rows[1]["resolved"] is True
    assert persistence.mistake_cause_counts() == {}   # ours is resolved
    assert persistence.mistake_cause_counts(app=None) == {"misread": 1}


def test_cause_counts_group_uncategorised_under_empty_key(data_dir):
    persistence.log_mistake(_entry("a"))
    persistence.log_mistake(_entry("b"))
    persistence.set_mistake_cause("b", "didnt_know")
    persistence.log_mistake(_entry("c"))
    persistence.set_mistake_cause("c", "didnt_know")
    assert persistence.mistake_cause_counts() == {"": 1, "didnt_know": 2}
    persistence.resolve_mistakes("b")
    assert persistence.mistake_cause_counts() == {"": 1, "didnt_know": 1}
    assert persistence.mistake_cause_counts(unresolved_only=False) == {
        "": 1, "didnt_know": 2}


# -------------------------------------------------------------- calibration

def test_confidence_entry_schema_and_clamping(data_dir):
    before = time.time()
    e = persistence.make_confidence_entry("sam_basic", "Sampler", 3, True)
    assert not data_dir.exists()                      # pure
    assert set(e) == CONFIDENCE_KEYS
    assert (e["id"], e["app"], e["category"]) == ("sam_basic", "qiskit-dojo", "Sampler")
    assert e["confidence"] == 3 and e["correct"] is True
    assert isinstance(e["timestamp"], float) and e["timestamp"] >= before - 1
    assert persistence.make_confidence_entry("k", "S", 9, False)["confidence"] == 4
    assert persistence.make_confidence_entry("k", "S", 0, False)["confidence"] == 1
    assert persistence.make_confidence_entry("k", "S", "x", False)["confidence"] == 1


def test_log_confidence_appends_every_pairing(data_dir):
    persistence.log_confidence("sam_basic", "Sampler", 4, False)
    persistence.log_confidence("sam_basic", "Sampler", 2, True)
    rows = _confidence(data_dir)
    assert [(r["confidence"], r["correct"]) for r in rows] == [(4, False), (2, True)]
    assert all(set(r) == CONFIDENCE_KEYS for r in rows)
    assert persistence.confidence_for_app("quantum-quiz") == []


def test_calibration_summary_and_confidently_wrong(data_dir):
    for level, correct in [(4, False), (4, True), (3, False), (1, False), (1, True)]:
        persistence.log_confidence("k", "Sampler", level, correct)
    assert persistence.calibration_summary() == {
        1: {"total": 2, "correct": 1},
        3: {"total": 1, "correct": 0},
        4: {"total": 2, "correct": 1},
    }
    wrong = persistence.confidently_wrong()
    assert [r["confidence"] for r in wrong] == [4, 3]     # the unknown unknowns
    assert persistence.confidently_wrong(threshold=4) == [wrong[0]]


# -------------------------------------------------- robustness + housekeeping

@pytest.mark.parametrize("junk", ["{not json", "[1, 2, 3]", '{"a": 1}', ""])
def test_corrupt_analytics_files_read_as_empty_and_recover(data_dir, junk):
    data_dir.mkdir(parents=True, exist_ok=True)
    persistence.MISTAKES_FILE.write_text(junk)
    persistence.CONFIDENCE_FILE.write_text(junk)
    persistence.SETTINGS_FILE.write_text(junk)
    assert persistence.load_mistakes() == []
    assert persistence.load_confidence() == []
    # a valid JSON object is a legal settings file; anything else reads as {}
    assert persistence.load_settings() == (
        json.loads(junk) if junk == '{"a": 1}' else {})
    assert persistence.mistake_cause_counts() == {}
    assert persistence.calibration_summary() == {}
    assert persistence.confidence_prompt_enabled() is True

    persistence.log_mistake(_entry())                 # writes over the junk
    persistence.log_confidence("k", "Sampler", 2, True)
    assert len(_mistakes(data_dir)) == 1
    assert len(_confidence(data_dir)) == 1


def test_missing_files_are_not_conjured_up_by_readers(data_dir):
    assert persistence.load_mistakes() == []
    assert persistence.load_confidence() == []
    assert persistence.load_settings() == {}
    assert not data_dir.exists()


def test_rows_are_capped_and_no_temp_files_survive(data_dir, monkeypatch):
    monkeypatch.setattr(persistence, "MAX_MISTAKES", 3)
    monkeypatch.setattr(persistence, "MAX_CONFIDENCE", 3)
    for i in range(6):
        persistence.log_mistake(_entry(f"k{i}"))
        persistence.log_confidence(f"k{i}", "Sampler", 2, True)
    assert [r["id"] for r in _mistakes(data_dir)] == ["k3", "k4", "k5"]
    assert [r["id"] for r in _confidence(data_dir)] == ["k3", "k4", "k5"]
    # The ".lock" sidecars are journal_sync's: empty files flock()ed for the
    # length of each read-modify-write on the shared journals, so a second app
    # cannot clobber rows we just wrote.
    assert sorted(p.name for p in data_dir.iterdir()) == [
        "confidence.json", "confidence.json.lock",
        "mistakes.json", "mistakes.json.lock"]


def test_writes_are_atomic(data_dir, monkeypatch):
    """A failure partway through a write leaves the old file intact."""
    persistence.log_mistake(_entry("safe"))
    good = persistence.MISTAKES_FILE.read_text()

    real_replace = persistence.os.replace
    monkeypatch.setattr(persistence.os, "replace",
                        lambda *a, **k: (_ for _ in ()).throw(OSError("disk full")))
    with pytest.raises(OSError):
        persistence.log_mistake(_entry("lost"))
    monkeypatch.setattr(persistence.os, "replace", real_replace)

    assert persistence.MISTAKES_FILE.read_text() == good
    assert [r["id"] for r in persistence.load_mistakes()] == ["safe"]
    assert sorted(p.name for p in data_dir.iterdir()) == [
        "mistakes.json", "mistakes.json.lock"]      # the lock sidecar, no temp files
    assert (data_dir / "mistakes.json.lock").read_bytes() == b""


# ------------------------------------------------------------------ settings

def test_confidence_prompt_opt_out_round_trips(data_dir):
    assert persistence.confidence_prompt_enabled() is True
    persistence.set_confidence_prompt_enabled(False)
    assert json.loads((data_dir / "dojo_settings.json").read_text()) == {
        "confidence_prompt": False}
    assert persistence.confidence_prompt_enabled() is False
    persistence.set_confidence_prompt_enabled(True)
    assert persistence.confidence_prompt_enabled() is True


def test_settings_preserve_unknown_keys(data_dir):
    persistence.save_settings({"future_key": 7})
    persistence.set_confidence_prompt_enabled(False)
    assert persistence.load_settings() == {"future_key": 7, "confidence_prompt": False}


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


def test_a_foreign_row_keeps_its_unknown_keys_through_our_writes(data_dir):
    """Another app's rows come back byte for byte — extra keys included.

    Both files are shared, so a rewrite here must put every row this app does
    not own back exactly as it was read.  Normalising a foreign row through
    this app's schema would silently drop whatever the owning app added to it.
    """
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "mistakes.json").write_text(json.dumps([FOREIGN_MISTAKE_ROW]))
    (data_dir / "confidence.json").write_text(json.dumps([FOREIGN_CONFIDENCE_ROW]))

    persistence.log_mistake(_entry("ours"))
    persistence.set_mistake_cause("ours", "misread")
    persistence.resolve_mistakes("ours")
    persistence.log_confidence("ours", "Results analysis", 3, False)

    mistakes = json.loads((data_dir / "mistakes.json").read_text())
    assert mistakes[0] == FOREIGN_MISTAKE_ROW      # unchanged, unknown keys intact
    assert len(mistakes) > 1                       # and our own row was written
    assert {r["app"] for r in mistakes[1:]} == {"qiskit-dojo"}
    confidence = json.loads((data_dir / "confidence.json").read_text())
    assert confidence[0] == FOREIGN_CONFIDENCE_ROW
    assert len(confidence) > 1
    assert {r["app"] for r in confidence[1:]} == {"qiskit-dojo"}
