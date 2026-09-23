"""Mistake journal + confidence calibration persistence (no Qt needed).

Contract under test (shared by every app in the suite):

    mistakes.json    [ {id, app, category, question, your_answer,
                        correct_answer, cause, note, timestamp, resolved}, … ]
    confidence.json  [ {id, app, category, confidence, correct, timestamp}, … ]
"""
from __future__ import annotations

import json
import time

import pytest

import common_path  # noqa: F401  (puts the repo root on sys.path)
from common import journal, jsonio

import persistence

MISTAKE_KEYS = {
    "id", "app", "category", "question", "your_answer", "correct_answer",
    "cause", "note", "timestamp", "resolved",
}
CONFIDENCE_KEYS = {"id", "app", "category", "confidence", "correct", "timestamp"}


def _mistake_file() -> list:
    return json.loads(persistence.mistakes_file().read_text())


def _confidence_file() -> list:
    return json.loads(persistence.confidence_file().read_text())


def _log(item_id: str = "abc123", category: str = "Qiskit", **kw) -> dict:
    kw.setdefault("question", "What does SamplerV2 return?")
    kw.setdefault("your_answer", "a Counts object")
    kw.setdefault("correct_answer", "a PrimitiveResult of PubResults")
    return persistence.log_mistake(item_id, category, **kw)


# ── Paths and vocabulary ──────────────────────────────────────────────────────

def test_new_paths_are_redirected_and_named_per_contract(data_dir):
    assert persistence.mistakes_file().is_relative_to(data_dir)
    assert persistence.confidence_file().is_relative_to(data_dir)
    assert persistence.settings_file().is_relative_to(data_dir)
    assert persistence.mistakes_file().name == "mistakes.json"
    assert persistence.confidence_file().name == "confidence.json"
    assert persistence.settings_file().name == "quiz_settings.json"
    assert persistence.APP_ID == "quantum-quiz"
    assert not data_dir.exists()          # importing never creates the directory


def test_cause_vocabulary_is_exactly_the_contract():
    assert persistence.MISTAKE_CAUSES == (
        "misread", "didnt_know", "knew_but_slipped", "confused", "out_of_time", "other",
    )
    assert set(persistence.CAUSE_LABELS) == set(persistence.MISTAKE_CAUSES)
    assert set(persistence.CONFIDENCE_LABELS) == {1, 2, 3, 4}
    assert persistence.normalise_cause("misread") == "misread"
    assert persistence.normalise_cause(None) is None
    assert persistence.normalise_cause("nonsense") is None
    assert persistence.normalise_cause("") is None


def test_item_id_is_content_stable_and_subject_scoped():
    a = persistence.mistake_item_id("Qiskit", "Explain   SamplerV2\nresult access.")
    b = persistence.mistake_item_id("Qiskit", "Explain SamplerV2 result access.")
    c = persistence.mistake_item_id("QASM", "Explain SamplerV2 result access.")
    d = persistence.mistake_item_id("Qiskit", "Explain EstimatorV2 result access.")
    assert a == b                                   # whitespace-insensitive
    assert a != c and a != d                        # subject and text both matter
    assert len(a) == 16 and all(ch in "0123456789abcdef" for ch in a)


# ── make_mistake_entry (pure) ─────────────────────────────────────────────────

def test_make_mistake_entry_shape_and_truncation():
    entry = persistence.make_mistake_entry(
        "id1", "Qiskit", "  q  " + "x" * 400, "y" * 400, "z" * 400,
        cause="bogus", note="n" * 700, timestamp=123.0,
    )
    assert set(entry) == MISTAKE_KEYS
    assert entry["id"] == "id1" and entry["app"] == "quantum-quiz"
    assert entry["category"] == "Qiskit"
    for field in ("question", "your_answer", "correct_answer"):
        assert len(entry[field]) == 200 and entry[field].endswith("…")
    assert journal.NOTE_MAX == persistence.NOTE_MAX == 500   # the suite-wide cap
    assert len(entry["note"]) == persistence.NOTE_MAX and entry["note"].endswith("…")
    # a note is prose the learner typed: its line breaks survive, unlike the
    # one-line fields above, which are collapsed so a list row cannot break
    multiline = persistence.make_mistake_entry("id3", "Q", "q", "a", "b",
                                               note="first\nsecond")
    assert multiline["note"] == "first\nsecond"
    assert entry["cause"] is None                   # unknown cause → uncategorised
    assert entry["timestamp"] == 123.0
    assert entry["resolved"] is False
    json.dumps(entry)                               # JSON-serialisable as-is

    ok = persistence.make_mistake_entry("id2", "QASM", "q", "a", "b",
                                        cause="knew_but_slipped", note=" note ")
    # only trailing space is stripped: the note is not reflowed
    assert ok["cause"] == "knew_but_slipped" and ok["note"] == " note"
    assert abs(ok["timestamp"] - time.time()) < 60


# ── Journal round trip ────────────────────────────────────────────────────────

def test_log_mistake_writes_one_entry_field_for_field(data_dir):
    entry = _log()
    stored = _mistake_file()
    assert stored == [entry]
    assert set(entry) == MISTAKE_KEYS
    assert entry["id"] == "abc123" and entry["app"] == "quantum-quiz"
    assert entry["category"] == "Qiskit"
    assert entry["question"] == "What does SamplerV2 return?"
    assert entry["your_answer"] == "a Counts object"
    assert entry["correct_answer"] == "a PrimitiveResult of PubResults"
    assert entry["cause"] is None                   # skipping loses nothing
    assert entry["note"] == "" and entry["resolved"] is False
    assert isinstance(entry["timestamp"], float)
    assert persistence.load_mistakes() == [entry]


def test_cause_and_note_update_the_same_entry(data_dir):
    _log()
    assert persistence.set_mistake_cause("abc123", "misread", note="read |0> as |1>")
    stored = _mistake_file()
    assert len(stored) == 1
    assert stored[0]["cause"] == "misread"
    assert stored[0]["note"] == "read |0> as |1>"
    assert persistence.mistake_cause_counts() == {"misread": 1}

    persistence.set_mistake_cause("abc123", None)   # cleared, note untouched
    assert _mistake_file()[0]["cause"] is None
    assert _mistake_file()[0]["note"] == "read |0> as |1>"
    assert persistence.mistake_cause_counts() == {"uncategorised": 1}

    assert persistence.set_mistake_cause("no-such-id", "other") is False


def test_a_repeat_miss_is_its_own_row(data_dir):
    """Three slips on one item are three rows: repetition is the signal.

    This is the suite-wide reconciliation (see common/README.md): merging a
    repeat into the open row destroys the count ``coach --mistakes`` and the
    dashboard report.  The earlier categorisation stays on the earlier row.
    """
    _log()
    persistence.set_mistake_cause("abc123", "didnt_know", note="revise PUBs")
    again = _log(your_answer="still a Counts object")
    stored = _mistake_file()
    assert len(stored) == 2
    assert stored[0]["cause"] == "didnt_know" and stored[0]["note"] == "revise PUBs"
    assert again["your_answer"] == "still a Counts object"
    assert again["cause"] is None and again["note"] == ""
    assert again["resolved"] is False
    assert persistence.mistake_cause_counts() == {"didnt_know": 1, "uncategorised": 1}
    # categorising now targets the newest open row, not the old one
    persistence.set_mistake_cause("abc123", "misread")
    stored = _mistake_file()
    assert [e["cause"] for e in stored] == ["didnt_know", "misread"]
    # …and resolving closes every open row for the item
    assert persistence.resolve_mistake("abc123") is True
    assert [e["resolved"] for e in _mistake_file()] == [True, True]
    assert persistence.get_mistake("abc123")["cause"] == "misread"   # newest


def test_resolve_marks_by_app_and_id_only(data_dir):
    _log()
    _log(item_id="other-item")
    jsonio.atomic_write_json(persistence.mistakes_file(), _mistake_file() + [
        {"id": "abc123", "app": "quantum-tutor", "cause": None, "resolved": False},
    ])
    assert persistence.resolve_mistake("abc123") is True
    stored = _mistake_file()
    assert [(e["id"], e["app"], e["resolved"]) for e in stored] == [
        ("abc123", "quantum-quiz", True),
        ("other-item", "quantum-quiz", False),
        ("abc123", "quantum-tutor", False),         # another app's row untouched
    ]
    assert persistence.resolve_mistake("abc123") is False     # idempotent, no rewrite
    assert [e["id"] for e in persistence.unresolved_mistakes("quantum-quiz")] == ["other-item"]


def test_cause_counts_ignore_resolved_unless_asked(data_dir):
    for i, cause in enumerate(["misread", "misread", "didnt_know"]):
        _log(item_id=f"i{i}")
        persistence.set_mistake_cause(f"i{i}", cause)
    _log(item_id="i3")                              # uncategorised
    persistence.resolve_mistake("i0")
    assert persistence.mistake_cause_counts() == {
        "misread": 1, "didnt_know": 1, "uncategorised": 1,
    }
    assert persistence.mistake_cause_counts(include_resolved=True) == {
        "misread": 2, "didnt_know": 1, "uncategorised": 1,
    }


def test_journal_tolerates_missing_corrupt_and_malformed(data_dir):
    assert persistence.load_mistakes() == []
    assert persistence.mistake_cause_counts() == {}
    assert persistence.get_mistake("abc123") is None
    assert persistence.resolve_mistake("abc123") is False
    assert persistence.set_mistake_cause("abc123", "other") is False

    data_dir.mkdir(parents=True)
    persistence.mistakes_file().write_text("not json")
    assert persistence.load_mistakes() == []
    persistence.mistakes_file().write_text(json.dumps({"id": "not-a-list"}))
    assert persistence.load_mistakes() == []
    persistence.mistakes_file().write_text(json.dumps(
        [{"id": "keep", "app": "quantum-quiz"}, {"no": "id"}, "bare", 7, None]
    ))
    # rows with no id cannot be matched or shown, so they are not loaded …
    assert [e["id"] for e in persistence.load_mistakes()] == ["keep"]
    _log()                                          # a write still succeeds
    assert _mistake_file()[-1]["id"] == "abc123"
    assert [e["id"] for e in persistence.load_mistakes()] == ["keep", "abc123"]
    # … but an object row is still written back, unknown keys and all
    assert {"no": "id"} in _mistake_file()


def test_writes_preserve_rows_from_other_apps(data_dir):
    data_dir.mkdir(parents=True)
    foreign = [{"id": "abc123", "app": "quantum-tutor", "cause": "confused"},
               {"id": "t2", "app": "quantum-tutor", "private": {"deep": 1}}]
    persistence.mistakes_file().write_text(json.dumps(foreign))
    _log()
    stored = _mistake_file()
    assert stored[:2] == foreign                    # verbatim, unknown keys intact
    assert stored[2]["id"] == "abc123" and stored[2]["app"] == "quantum-quiz"
    persistence.set_mistake_cause("abc123", "other")
    assert _mistake_file()[:2] == foreign
    assert _mistake_file()[2]["cause"] == "other"   # ours, not the tutor's


def test_journal_growth_is_capped(data_dir, monkeypatch):
    monkeypatch.setattr(journal, "MISTAKES_MAX", 5)
    for i in range(8):
        _log(item_id=f"item{i}")
    stored = _mistake_file()
    assert len(stored) == 5
    assert [e["id"] for e in stored] == [f"item{i}" for i in range(3, 8)]   # oldest dropped


def test_writes_are_atomic_and_leave_no_temp_files(data_dir):
    _log()
    persistence.log_confidence("abc123", "Qiskit", 3, False)
    persistence.set_confidence_prompt_enabled(False)
    leftovers = [p.name for p in data_dir.iterdir() if p.name.endswith(".tmp")]
    assert leftovers == []
    # ".lock" sidecars are common.locking's: empty files that exist only to be
    # flock()ed for the length of a read-modify-write, so a second app (or a
    # second window) cannot clobber rows we just appended.  ".schema.json"
    # sidecars are common.schema's version stamps — they sit *beside* the data
    # so every existing reader, which opens one exact file name, is unaffected.
    assert sorted(p.name for p in data_dir.iterdir()) == [
        "confidence.json", "confidence.json.lock", "confidence.json.schema.json",
        "mistakes.json", "mistakes.json.lock", "mistakes.json.schema.json",
        "quiz_settings.json", "quiz_settings.json.lock",
        "quiz_settings.json.schema.json",
    ]
    assert (data_dir / "mistakes.json.lock").read_bytes() == b""


def test_a_failed_write_keeps_the_previous_file_intact(data_dir, monkeypatch):
    _log()
    good = _mistake_file()

    def boom(*_a, **_k):
        raise OSError("disk full")

    monkeypatch.setattr(jsonio.os, "replace", boom)
    with pytest.raises(OSError):
        _log(item_id="never-lands")
    assert _mistake_file() == good                  # old content still there
    assert [p.name for p in data_dir.iterdir() if p.name.endswith(".tmp")] == []


# ── Confidence calibration ────────────────────────────────────────────────────

def test_make_confidence_entry_shape_and_clamping():
    e = persistence.make_confidence_entry("id1", "Qiskit", 3, True, timestamp=9.0)
    assert set(e) == CONFIDENCE_KEYS
    assert (e["id"], e["app"], e["category"]) == ("id1", "quantum-quiz", "Qiskit")
    assert e["confidence"] == 3 and e["correct"] is True and e["timestamp"] == 9.0
    assert persistence.make_confidence_entry("i", "c", 99, False)["confidence"] == 4
    assert persistence.make_confidence_entry("i", "c", 0, False)["confidence"] == 1
    assert persistence.make_confidence_entry("i", "c", "x", False)["confidence"] == 1
    assert persistence.make_confidence_entry("i", "c", 2, 1)["correct"] is True


def test_log_confidence_appends_pairings(data_dir):
    first = persistence.log_confidence("id1", "Qiskit", 4, False)
    persistence.log_confidence("id2", "QASM", 2, True)
    rows = _confidence_file()
    assert rows[0] == first and len(rows) == 2
    assert [r["confidence"] for r in rows] == [4, 2]
    assert [r["correct"] for r in rows] == [False, True]
    assert persistence.load_confidence() == rows
    assert persistence.load_confidence("quantum-tutor") == []


def test_calibration_and_confidently_wrong(data_dir):
    for conf, correct, cat in [(4, False, "Qiskit"), (4, False, "Qiskit"),
                               (4, True, "Qiskit"), (3, False, "QASM"),
                               (1, False, "QASM"), (1, True, "QASM")]:
        persistence.log_confidence("id", cat, conf, correct)
    calibration = persistence.confidence_calibration()
    assert calibration[4] == {"n": 3, "correct": 1, "accuracy": pytest.approx(1 / 3)}
    assert calibration[3] == {"n": 1, "correct": 0, "accuracy": 0.0}
    assert calibration[1] == {"n": 2, "correct": 1, "accuracy": 0.5}
    assert 2 not in calibration
    # "sure but wrong" ignores the honest guesses (confidence 1-2)
    assert persistence.confidently_wrong() == {"Qiskit": 2, "QASM": 1}
    assert persistence.confidently_wrong(min_confidence=4) == {"Qiskit": 2}


def test_confidence_tolerates_missing_corrupt_and_malformed(data_dir):
    assert persistence.load_confidence() == []
    assert persistence.confidence_calibration() == {}
    assert persistence.confidently_wrong() == {}
    data_dir.mkdir(parents=True)
    persistence.confidence_file().write_text("{{{")
    assert persistence.load_confidence() == []
    persistence.confidence_file().write_text(json.dumps(
        [{"id": "a", "confidence": 3, "correct": True}, {"id": "b"}, {"confidence": 2}, "x"]
    ))
    assert [r["id"] for r in persistence.load_confidence()] == ["a"]
    persistence.log_confidence("c", "Qiskit", 1, False)
    rows = _confidence_file()
    # every object row is written back untouched; the bare string "x" is not a
    # row any reader in the suite can use, and does not survive the rewrite
    assert rows[:3] == [{"id": "a", "confidence": 3, "correct": True},
                        {"id": "b"}, {"confidence": 2}]
    assert rows[3]["id"] == "c" and len(rows) == 4


def test_an_out_of_range_rating_records_nothing(data_dir):
    """Clamping would invent a rating and then report on it; reject instead."""
    assert persistence.log_confidence("id1", "Qiskit", 0, True) is None
    assert persistence.log_confidence("id1", "Qiskit", 9, True) is None
    assert persistence.log_confidence("id1", "Qiskit", None, True) is None
    assert not persistence.confidence_file().exists()
    assert persistence.log_confidence("id1", "Qiskit", 2, True) is not None
    assert [r["confidence"] for r in _confidence_file()] == [2]


def test_confidence_growth_is_capped(data_dir, monkeypatch):
    monkeypatch.setattr(journal, "CONFIDENCE_MAX", 3)
    for i in range(6):
        persistence.log_confidence(f"id{i}", "Qiskit", 2, True)
    assert [r["id"] for r in _confidence_file()] == ["id3", "id4", "id5"]


# ── App settings (confidence opt-out) ─────────────────────────────────────────

def test_confidence_prompt_opt_out_round_trip(data_dir):
    assert persistence.load_settings() == {}
    assert persistence.confidence_prompt_enabled() is True      # default: ask
    persistence.set_confidence_prompt_enabled(False)
    assert json.loads(persistence.settings_file().read_text()) == {
        "confidence_prompt_enabled": False
    }
    assert persistence.confidence_prompt_enabled() is False
    persistence.set_setting("unrelated", 7)
    persistence.set_confidence_prompt_enabled(True)
    assert persistence.load_settings() == {
        "confidence_prompt_enabled": True, "unrelated": 7,
    }
    assert persistence.confidence_prompt_enabled() is True


def test_settings_tolerate_corrupt_file(data_dir):
    data_dir.mkdir(parents=True)
    persistence.settings_file().write_text("not json")
    assert persistence.load_settings() == {}
    assert persistence.confidence_prompt_enabled() is True
    persistence.settings_file().write_text(json.dumps(["a", "list"]))
    assert persistence.load_settings() == {}
    persistence.set_confidence_prompt_enabled(False)            # recovers cleanly
    assert persistence.load_settings() == {"confidence_prompt_enabled": False}


def test_existing_history_files_are_untouched_by_the_new_writers(data_dir):
    """The new files must never disturb the load-bearing history schemas."""
    _log()
    persistence.log_confidence("abc123", "Qiskit", 4, False)
    assert not persistence.history_file().exists()
    assert not persistence.flagged_file().exists()
    assert not persistence.draft_file().exists()


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

    _log("ours")
    persistence.set_mistake_cause("ours", "misread")
    persistence.resolve_mistake("ours")
    persistence.log_confidence("ours", "Qiskit", 3, False)

    mistakes = json.loads((data_dir / "mistakes.json").read_text())
    assert mistakes[0] == FOREIGN_MISTAKE_ROW      # unchanged, unknown keys intact
    assert len(mistakes) > 1                       # and our own row was written
    assert {r["app"] for r in mistakes[1:]} == {"quantum-quiz"}
    confidence = json.loads((data_dir / "confidence.json").read_text())
    assert confidence[0] == FOREIGN_CONFIDENCE_ROW
    assert len(confidence) > 1
    assert {r["app"] for r in confidence[1:]} == {"quantum-quiz"}
