"""Mistake journal + confidence calibration: the pure helpers and the two
shared JSON stores, exercised against a temp data dir (never the real one).

Both files (``mistakes.json`` and ``confidence.json``) are shared with the
other nine apps, so every test that writes also checks that a foreign app's
rows survive untouched.
"""
from __future__ import annotations

import json
import time

import pytest

import persistence
from config import APP_ID

MISTAKE_KEYS = {"id", "app", "category", "question", "your_answer",
                "correct_answer", "cause", "note", "timestamp", "resolved"}
CONFIDENCE_KEYS = {"id", "app", "category", "confidence", "correct", "timestamp"}

FOREIGN_MISTAKE = {
    "id": "quiz-abc", "app": "quantum-quiz", "category": "Gates",
    "question": "q", "your_answer": "a", "correct_answer": "b",
    "cause": "misread", "note": "", "timestamp": 1.0, "resolved": False,
}
FOREIGN_CONFIDENCE = {
    "id": "quiz-abc", "app": "quantum-quiz", "category": "Gates",
    "confidence": 2, "correct": True, "timestamp": 1.0,
}


def _write(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload if isinstance(payload, str) else json.dumps(payload))


# ---------------------------------------------------------------------------
# Pure helpers
# ---------------------------------------------------------------------------

def test_clip_text_collapses_whitespace_and_truncates():
    assert persistence.clip_text("  two   lines\nhere ") == "two lines here"
    assert persistence.clip_text(None) == ""
    exact = "x" * persistence.MISTAKE_TEXT_MAX
    assert persistence.clip_text(exact) == exact
    clipped = persistence.clip_text("y" * 500)
    assert len(clipped) == persistence.MISTAKE_TEXT_MAX == 200
    assert clipped.endswith("…")
    assert persistence.clip_text("abcdef", 4) == "abc…"


def test_normalise_cause_accepts_only_contract_values():
    assert persistence.MISTAKE_CAUSES == (
        "misread", "didnt_know", "knew_but_slipped", "confused",
        "out_of_time", "other",
    )
    for cause in persistence.MISTAKE_CAUSES:
        assert persistence.normalise_cause(cause) == cause
        assert cause in persistence.MISTAKE_CAUSE_LABELS
    for bad in (None, "", "nonsense", 3, True):
        assert persistence.normalise_cause(bad) is None


def test_make_mistake_entry_matches_contract_field_for_field():
    before = time.time()
    entry = persistence.make_mistake_entry(
        "paper-0123456789abcdef", "Surface Codes", "  Why  does it work?\n",
        "z" * 400, "because " * 60, cause="knew_but_slipped", note="  bit order  ",
    )
    assert set(entry) == MISTAKE_KEYS
    assert entry["id"] == "paper-0123456789abcdef"
    assert entry["app"] == APP_ID == "paper-drill"
    assert entry["category"] == "Surface Codes"
    assert entry["question"] == "Why does it work?"
    assert len(entry["your_answer"]) == 200 and entry["your_answer"].endswith("…")
    assert len(entry["correct_answer"]) == 200
    assert entry["cause"] == "knew_but_slipped"
    assert entry["note"] == "bit order"
    assert isinstance(entry["timestamp"], float)
    assert before <= entry["timestamp"] <= time.time() + 1
    assert entry["resolved"] is False

    # Unknown cause degrades to "logged but not categorised", never a crash.
    assert persistence.make_mistake_entry("i", "c", "q", "a", "b",
                                          cause="banana")["cause"] is None
    fixed = persistence.make_mistake_entry("i", "c", "q", "a", "b",
                                           timestamp=5, resolved=1)
    assert fixed["timestamp"] == 5.0 and fixed["resolved"] is True


def test_make_confidence_entry_matches_contract_field_for_field():
    entry = persistence.make_confidence_entry("paper-1", "Paper A", 4, False)
    assert set(entry) == CONFIDENCE_KEYS
    assert entry["id"] == "paper-1"
    assert entry["app"] == APP_ID
    assert entry["category"] == "Paper A"
    assert entry["confidence"] == 4
    assert entry["correct"] is False
    assert isinstance(entry["timestamp"], float)
    assert persistence.CONFIDENCE_LEVELS == {
        1: "Guessing", 2: "Unsure", 3: "Fairly sure", 4: "Certain"}


def test_cause_counts_tallies_and_separates_uncategorised():
    rows = [
        persistence.make_mistake_entry("a", "c", "q", "y", "z", cause="misread"),
        persistence.make_mistake_entry("b", "c", "q", "y", "z", cause="misread"),
        persistence.make_mistake_entry("c", "c", "q", "y", "z"),
        persistence.make_mistake_entry("d", "c", "q", "y", "z",
                                       cause="confused", resolved=True),
        dict(FOREIGN_MISTAKE),
    ]
    assert persistence.cause_counts(rows) == {
        "misread": 2, "uncategorised": 1, "confused": 1}
    assert persistence.cause_counts(rows, include_resolved=False) == {
        "misread": 2, "uncategorised": 1}
    assert persistence.cause_counts(rows, app=None)["misread"] == 3


def test_confidently_wrong_picks_the_unknown_unknowns():
    rows = [
        persistence.make_confidence_entry("a", "c", 4, False),   # confidently wrong
        persistence.make_confidence_entry("b", "c", 3, False),   # confidently wrong
        persistence.make_confidence_entry("c", "c", 2, False),   # knew it was shaky
        persistence.make_confidence_entry("d", "c", 4, True),    # right and knew it
        {"id": "e", "app": APP_ID, "confidence": "4", "correct": False},
        dict(FOREIGN_CONFIDENCE, confidence=4, correct=False),
    ]
    assert [e["id"] for e in persistence.confidently_wrong(rows)] == ["a", "b"]
    assert len(persistence.confidently_wrong(rows, app=None)) == 3


# ---------------------------------------------------------------------------
# Mistake journal store
# ---------------------------------------------------------------------------

class TestMistakeStore:
    def test_log_mistake_writes_contract_entry(self, data_dir):
        assert persistence.MISTAKES_FILE == data_dir / "mistakes.json"
        assert persistence.load_mistakes() == []

        before = time.time()
        returned = persistence.log_mistake(
            "paper-aaaa", "Paper A", "What is d?", "three", "five")
        entries = json.loads(persistence.MISTAKES_FILE.read_text())
        assert entries == [returned]
        entry = entries[0]
        assert set(entry) == MISTAKE_KEYS
        assert entry["id"] == "paper-aaaa"
        assert entry["app"] == "paper-drill"
        assert entry["category"] == "Paper A"
        assert entry["question"] == "What is d?"
        assert entry["your_answer"] == "three"
        assert entry["correct_answer"] == "five"
        assert entry["cause"] is None          # skipping the row loses nothing
        assert entry["note"] == ""
        assert entry["resolved"] is False
        assert before <= entry["timestamp"] <= time.time() + 1

    def test_each_slip_is_its_own_row_and_causes_update_the_newest(self, data_dir):
        persistence.log_mistake("paper-a", "P", "Q", "wrong1", "right")
        persistence.log_mistake("paper-a", "P", "Q", "wrong2", "right")
        assert len(persistence.mistakes_for("paper-a")) == 2

        assert persistence.set_mistake_cause("paper-a", "misread", "swapped order") is True
        rows = persistence.mistakes_for("paper-a")
        assert [r["cause"] for r in rows] == [None, "misread"]
        assert rows[-1]["note"] == "swapped order"
        assert rows[-1]["your_answer"] == "wrong2"

        # Re-picking overwrites the same row instead of piling up duplicates.
        persistence.set_mistake_cause("paper-a", "confused")
        rows = persistence.mistakes_for("paper-a")
        assert len(rows) == 2
        assert rows[-1]["cause"] == "confused" and rows[-1]["note"] == ""
        # Clearing the cause is allowed (back to "logged, not categorised").
        persistence.set_mistake_cause("paper-a", None, "note only")
        assert persistence.mistakes_for("paper-a")[-1] == {
            **rows[-1], "cause": None, "note": "note only"}

    def test_set_cause_on_unknown_item_is_false_and_writes_nothing(self, data_dir):
        assert persistence.set_mistake_cause("paper-nope", "misread") is False
        assert not persistence.MISTAKES_FILE.exists()

    def test_resolve_marks_only_this_app_and_this_item(self, data_dir):
        _write(persistence.MISTAKES_FILE, [dict(FOREIGN_MISTAKE, id="paper-a")])
        persistence.log_mistake("paper-a", "P", "Q", "w", "r")
        persistence.log_mistake("paper-a", "P", "Q", "w2", "r")
        persistence.log_mistake("paper-b", "P", "Q2", "w", "r")

        assert persistence.resolve_mistake("paper-a") == 2
        assert persistence.resolve_mistake("paper-a") == 0      # idempotent
        entries = persistence.load_mistakes()
        assert [(e["app"], e["id"], e["resolved"]) for e in entries] == [
            ("quantum-quiz", "paper-a", False),                 # foreign untouched
            ("paper-drill", "paper-a", True),
            ("paper-drill", "paper-a", True),
            ("paper-drill", "paper-b", False),
        ]

    def test_resolved_row_is_reopened_by_a_fresh_slip(self, data_dir):
        persistence.log_mistake("paper-a", "P", "Q", "w", "r")
        persistence.set_mistake_cause("paper-a", "didnt_know")
        persistence.resolve_mistake("paper-a")
        persistence.log_mistake("paper-a", "P", "Q", "w again", "r")
        persistence.set_mistake_cause("paper-a", "knew_but_slipped")
        rows = persistence.mistakes_for("paper-a")
        assert [(r["cause"], r["resolved"]) for r in rows] == [
            ("didnt_know", True), ("knew_but_slipped", False)]

    def test_foreign_rows_survive_our_writes(self, data_dir):
        _write(persistence.MISTAKES_FILE, [FOREIGN_MISTAKE])
        persistence.log_mistake("paper-a", "P", "Q", "w", "r")
        persistence.set_mistake_cause("paper-a", "other", "note")
        persistence.resolve_mistake("paper-a")
        apps = [e["app"] for e in persistence.load_mistakes()]
        assert apps == ["quantum-quiz", "paper-drill"]
        assert persistence.load_mistakes()[0] == FOREIGN_MISTAKE

    @pytest.mark.parametrize("raw,expected", [
        ("{not json", 0),
        (json.dumps({"id": "x"}), 0),
        (json.dumps([{"no": "id"}, 7, None, FOREIGN_MISTAKE]), 1),
        ("", 0),
    ], ids=["corrupt", "non-list", "malformed-entries", "empty-file"])
    def test_load_tolerates_bad_files(self, data_dir, raw, expected):
        _write(persistence.MISTAKES_FILE, raw)
        assert len(persistence.load_mistakes()) == expected
        # and a write still recovers the file
        persistence.log_mistake("paper-a", "P", "Q", "w", "r")
        assert persistence.mistakes_for("paper-a")

    def test_missing_file_reads_empty(self, data_dir):
        assert persistence.load_mistakes() == []
        assert persistence.mistakes_for("anything") == []
        assert persistence.cause_counts() == {}
        assert not persistence.MISTAKES_FILE.exists()

    def test_cap_drops_our_oldest_rows_only(self, data_dir, monkeypatch):
        monkeypatch.setattr(persistence, "MISTAKES_MAX_ENTRIES", 3)
        _write(persistence.MISTAKES_FILE, [FOREIGN_MISTAKE])
        for n in range(5):
            persistence.log_mistake(f"paper-{n}", "P", "Q", "w", "r")
        entries = persistence.load_mistakes()
        assert len(entries) == 3
        assert entries[0] == FOREIGN_MISTAKE                     # never discarded
        assert [e["id"] for e in entries[1:]] == ["paper-3", "paper-4"]

    def test_writes_are_atomic_and_leave_no_temp_files(self, data_dir):
        persistence.log_mistake("paper-a", "P", "Q", "w", "r")
        persistence.log_confidence("paper-a", "P", 3, False)
        persistence.set_confidence_prompt_enabled(False)
        # The ".lock" sidecars are journal_sync's: empty files flock()ed for
        # the length of a read-modify-write on the two shared journals, so a
        # second app cannot clobber rows we just appended.
        assert sorted(p.name for p in data_dir.iterdir()) == [
            "confidence.json", "confidence.json.lock",
            "mistakes.json", "mistakes.json.lock", "paper_settings.json"]
        assert (data_dir / "mistakes.json.lock").read_bytes() == b""


# ---------------------------------------------------------------------------
# Confidence store
# ---------------------------------------------------------------------------

class TestConfidenceStore:
    def test_log_confidence_writes_contract_row(self, data_dir):
        assert persistence.CONFIDENCE_FILE == data_dir / "confidence.json"
        assert persistence.load_confidence() == []

        returned = persistence.log_confidence("paper-a", "Paper A", 4, False)
        rows = json.loads(persistence.CONFIDENCE_FILE.read_text())
        assert rows == [returned]
        row = rows[0]
        assert set(row) == CONFIDENCE_KEYS
        assert (row["id"], row["app"], row["category"]) == (
            "paper-a", "paper-drill", "Paper A")
        assert row["confidence"] == 4 and row["correct"] is False
        assert isinstance(row["timestamp"], float)

    @pytest.mark.parametrize("bad", [0, 5, -1, None, "", "high", [], 9.5])
    def test_out_of_range_rating_is_a_silent_no_op(self, data_dir, bad):
        assert persistence.log_confidence("paper-a", "P", bad, True) is None
        assert not persistence.CONFIDENCE_FILE.exists()

    def test_numeric_strings_and_bools_are_coerced_or_rejected(self, data_dir):
        assert persistence.log_confidence("paper-a", "P", "3", True)["confidence"] == 3
        assert persistence.log_confidence("paper-b", "P", True, True)["confidence"] == 1
        # a float is truncated, not rejected (the UI only ever sends 1-4 ints)
        assert persistence.log_confidence("paper-c", "P", 2.7, True)["confidence"] == 2

    def test_rows_accumulate_and_foreign_rows_survive(self, data_dir):
        _write(persistence.CONFIDENCE_FILE, [FOREIGN_CONFIDENCE])
        persistence.log_confidence("paper-a", "P", 1, True)
        persistence.log_confidence("paper-a", "P", 4, False)
        rows = persistence.load_confidence()
        assert [r["app"] for r in rows] == ["quantum-quiz", "paper-drill", "paper-drill"]
        assert [r["confidence"] for r in rows] == [2, 1, 4]
        assert [e["id"] for e in persistence.confidently_wrong()] == ["paper-a"]

    @pytest.mark.parametrize("raw", ["{not json", '{"id": "x"}', "", "[1, 2"])
    def test_load_tolerates_bad_files(self, data_dir, raw):
        _write(persistence.CONFIDENCE_FILE, raw)
        assert persistence.load_confidence() == []
        assert persistence.confidently_wrong() == []
        persistence.log_confidence("paper-a", "P", 2, True)
        assert len(persistence.load_confidence()) == 1

    def test_cap_drops_our_oldest_rows_only(self, data_dir, monkeypatch):
        monkeypatch.setattr(persistence, "CONFIDENCE_MAX_ENTRIES", 2)
        _write(persistence.CONFIDENCE_FILE, [FOREIGN_CONFIDENCE])
        for n in range(4):
            persistence.log_confidence(f"paper-{n}", "P", 2, True)
        rows = persistence.load_confidence()
        assert [r["id"] for r in rows] == ["quiz-abc", "paper-3"]


# ---------------------------------------------------------------------------
# App settings (the confidence-strip opt-out)
# ---------------------------------------------------------------------------

class TestSettings:
    def test_defaults_to_on_and_round_trips(self, data_dir):
        assert persistence.SETTINGS_FILE == data_dir / "paper_settings.json"
        assert persistence.load_settings() == {}
        assert persistence.confidence_prompt_enabled() is True

        persistence.set_confidence_prompt_enabled(False)
        assert json.loads(persistence.SETTINGS_FILE.read_text()) == {
            "confidence_prompt": False}
        assert persistence.confidence_prompt_enabled() is False

        persistence.set_confidence_prompt_enabled(True)
        assert persistence.confidence_prompt_enabled() is True

    def test_other_keys_are_preserved(self, data_dir):
        persistence.save_settings({"keep": "me"})
        persistence.set_confidence_prompt_enabled(False)
        assert persistence.load_settings() == {"keep": "me",
                                               "confidence_prompt": False}

    @pytest.mark.parametrize("raw", ["{not json", "[]", "null", ""])
    def test_bad_settings_file_reads_as_defaults(self, data_dir, raw):
        _write(persistence.SETTINGS_FILE, raw)
        assert persistence.load_settings() == {}
        assert persistence.confidence_prompt_enabled() is True


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

    persistence.log_mistake("ours", "P", "Q", "w", "r")
    persistence.set_mistake_cause("ours", "misread")
    persistence.resolve_mistake("ours")
    persistence.log_confidence("ours", "P", 3, False)

    mistakes = json.loads((data_dir / "mistakes.json").read_text())
    assert mistakes[0] == FOREIGN_MISTAKE_ROW      # unchanged, unknown keys intact
    assert len(mistakes) > 1                       # and our own row was written
    assert {r["app"] for r in mistakes[1:]} == {APP_ID}
    confidence = json.loads((data_dir / "confidence.json").read_text())
    assert confidence[0] == FOREIGN_CONFIDENCE_ROW
    assert len(confidence) > 1
    assert {r["app"] for r in confidence[1:]} == {APP_ID}
