"""mistakes.json / confidence.json / exam_settings.json helpers (no Qt).

The store underneath is ``common.journal`` (locked, atomic, foreign rows
preserved, each app trimming only its own rows); what is tested here is
exam-sim's adapter over it — Question -> row, the session journal, the home
screen's summary — plus the schema sidecar and the settings file.  Every test
runs against the temp ``data_dir``.
"""
import json

import pytest

import common_path  # noqa: F401  (puts the repo root on sys.path)

import persistence
from common import journal, schema
from core.models import ExamAttempt, ExamResult, Question

MISTAKE_KEYS = {"id", "app", "category", "question", "your_answer",
                "correct_answer", "cause", "note", "timestamp", "resolved"}
CONFIDENCE_KEYS = {"id", "app", "category", "confidence", "correct", "timestamp"}


def _q(qid: str, section: str = "Sampler", correct: int = 1) -> Question:
    return Question(id=qid, section=section, question=f"Question {qid}?",
                    options=["opt-a", "opt-b", "opt-c", "opt-d"],
                    correct_index=correct, explanation="because",
                    difficulty="easy")


# ----------------------------------------------------------- pure entry maker
def test_make_mistake_entry_has_the_shared_schema():
    entry = persistence.make_mistake_entry(
        "cc_depth", "Create circuits", "How deep?", "4", "3")
    assert set(entry) == MISTAKE_KEYS
    assert entry["id"] == "cc_depth"
    assert entry["app"] == "exam-sim"           # the app directory name
    assert entry["category"] == "Create circuits"
    assert entry["cause"] is None               # logged, not yet categorised
    assert entry["note"] == ""
    assert entry["resolved"] is False
    assert isinstance(entry["timestamp"], float)


def test_make_mistake_entry_clips_the_one_line_fields_to_200_chars():
    entry = persistence.make_mistake_entry(
        "x", "Sampler", "q" * 500, "a" * 500, "b" * 500, note="n" * 900)
    for field in ("question", "your_answer", "correct_answer"):
        assert len(entry[field]) == 200, field
        assert entry[field].endswith("…")
    # The note is prose the learner typed: 500 chars, and its line breaks are
    # kept (the one-line fields are collapsed so a list row cannot be broken).
    assert len(entry["note"]) == persistence.NOTE_LIMIT == 500
    assert entry["note"].endswith("…")
    assert persistence.make_mistake_entry(
        "x", "Sampler", "a\nb", "", "", note="one\ntwo") == {
        **entry, "question": "a b", "your_answer": "", "correct_answer": "",
        "note": "one\ntwo", "timestamp": pytest.approx(entry["timestamp"], abs=5)}


def test_make_mistake_entry_never_loses_the_row_over_an_unknown_cause():
    """Suite rule (common/README.md §3): a stray cause is stored as None.

    exam-sim used to raise ValueError here, which cost the mistake itself.
    A recognised cause still survives spacing and case.
    """
    entry = persistence.make_mistake_entry("x", "Sampler", "q", "a", "b",
                                           cause="because-i-said-so")
    assert entry["cause"] is None
    assert persistence.make_mistake_entry(
        "x", "Sampler", "q", "a", "b", cause=" Misread ")["cause"] == "misread"


def test_every_documented_cause_is_accepted():
    assert set(persistence.MISTAKE_CAUSES) == {
        "misread", "didnt_know", "knew_but_slipped", "confused",
        "out_of_time", "other"}
    for cause in persistence.MISTAKE_CAUSES:
        entry = persistence.make_mistake_entry("x", "Sampler", "q", "a", "b",
                                               cause=cause)
        assert entry["cause"] == cause
        assert cause in persistence.CAUSE_LABELS


def test_mistake_entry_for_maps_a_question_and_the_chosen_option():
    entry = persistence.mistake_entry_for(_q("s1"), 3)
    assert entry["your_answer"] == "opt-d"
    assert entry["correct_answer"] == "opt-b"
    assert entry["category"] == "Sampler"
    assert persistence.mistake_entry_for(_q("s1"), None)["your_answer"] == "(no answer)"


# ------------------------------------------------------------------ file I/O
def test_load_mistakes_is_empty_without_a_file(data_dir):
    assert persistence.load_mistakes() == []
    assert not persistence.MISTAKES_FILE.exists()


def test_log_mistake_appends_and_round_trips(data_dir):
    persistence.log_mistake(persistence.mistake_entry_for(_q("a"), 0))
    persistence.log_mistake(persistence.mistake_entry_for(_q("b"), 0))
    rows = json.loads(persistence.MISTAKES_FILE.read_text())
    assert [r["id"] for r in rows] == ["a", "b"]
    assert rows == persistence.load_mistakes()


def test_one_row_per_miss_occurrence_so_repeats_are_countable(data_dir):
    for _ in range(3):
        persistence.log_mistake(persistence.mistake_entry_for(_q("a"), 0))
    assert len(persistence.load_mistakes()) == 3


def test_update_mistake_cause_fills_in_the_newest_row(data_dir):
    persistence.log_mistake(persistence.mistake_entry_for(_q("a"), 0))
    old = persistence.log_mistake(persistence.mistake_entry_for(_q("a"), 2))
    assert persistence.update_mistake_cause("a", "misread", "swapped the bits")

    rows = persistence.load_mistakes()
    assert rows[0]["cause"] is None                 # older row untouched
    assert rows[1]["cause"] == "misread"
    assert rows[1]["note"] == "swapped the bits"
    assert rows[1]["timestamp"] == old["timestamp"]  # timestamp is the miss time


def test_update_mistake_cause_can_target_an_exact_timestamp(data_dir):
    first = persistence.log_mistake(persistence.mistake_entry_for(_q("a"), 0))
    persistence.log_mistake(persistence.mistake_entry_for(_q("a"), 2))
    assert persistence.update_mistake_cause("a", "confused",
                                            timestamp=first["timestamp"])
    rows = persistence.load_mistakes()
    assert rows[0]["cause"] == "confused"
    assert rows[1]["cause"] is None


def test_update_mistake_cause_returns_false_when_there_is_no_row(data_dir):
    assert persistence.update_mistake_cause("nope", "other") is False
    assert persistence.load_mistakes() == []


def test_update_mistake_cause_stores_an_unknown_cause_as_none(data_dir):
    persistence.log_mistake(persistence.mistake_entry_for(_q("a"), 0))
    persistence.update_mistake_cause("a", "misread")
    assert persistence.update_mistake_cause("a", "nonsense") is True
    assert persistence.load_mistakes()[0]["cause"] is None


def test_update_mistake_cause_ignores_other_apps(data_dir):
    other = persistence.make_mistake_entry("a", "Sampler", "q", "x", "y",
                                           app="quantum-quiz")
    persistence.log_mistake(other)
    assert persistence.update_mistake_cause("a", "other") is False
    assert persistence.load_mistakes()[0]["cause"] is None


def test_resolve_mistake_flips_every_row_for_the_item(data_dir):
    persistence.log_mistake(persistence.mistake_entry_for(_q("a"), 0))
    persistence.log_mistake(persistence.mistake_entry_for(_q("a"), 2))
    persistence.log_mistake(persistence.mistake_entry_for(_q("b"), 0))

    assert persistence.resolve_mistake("a") == 2
    rows = {(r["id"], r["resolved"]) for r in persistence.load_mistakes()}
    assert rows == {("a", True), ("b", False)}
    assert persistence.resolve_mistake("a") == 0     # idempotent, no rewrite


def test_resolve_mistake_keeps_the_cause_analysis(data_dir):
    persistence.log_mistake(persistence.mistake_entry_for(_q("a"), 0))
    persistence.update_mistake_cause("a", "didnt_know", "read chapter 7")
    persistence.resolve_mistake("a")
    row = persistence.load_mistakes()[0]
    assert row["resolved"] is True
    assert (row["cause"], row["note"]) == ("didnt_know", "read chapter 7")


def test_mistakes_file_is_capped_at_the_newest_rows(data_dir, monkeypatch):
    monkeypatch.setattr(journal, "MISTAKES_MAX", 5)
    for i in range(8):
        persistence.log_mistake(persistence.mistake_entry_for(_q(f"q{i}"), 0))
    ids = [r["id"] for r in persistence.load_mistakes()]
    assert ids == ["q3", "q4", "q5", "q6", "q7"]


def test_writes_are_atomic_and_leave_no_temp_file(data_dir):
    persistence.log_mistake(persistence.mistake_entry_for(_q("a"), 0))
    persistence.log_confidence("a", "Sampler", 3, True)
    persistence.set_confidence_enabled(False)
    assert [p.name for p in sorted(data_dir.glob("*.tmp"))] == []
    # The ".lock" sidecars are common.locking: empty files flock()ed for the
    # length of a read-modify-write on the shared journals, so another app
    # writing at the same time cannot drop the rows we just appended.  The
    # ".schema.json" sidecars are common.schema's version markers — a sidecar
    # rather than a key in the data, because coach.py and dashboard.py require
    # the top level of these files to be a plain JSON list.
    assert {p.name for p in data_dir.iterdir()} == {
        "mistakes.json", "mistakes.json.lock", "mistakes.json.schema.json",
        "confidence.json", "confidence.json.lock", "confidence.json.schema.json",
        "exam_settings.json", "exam_settings.json.schema.json"}
    assert (data_dir / "mistakes.json.lock").read_bytes() == b""


def test_corrupt_files_start_fresh_instead_of_crashing(data_dir):
    data_dir.mkdir(parents=True)
    persistence.MISTAKES_FILE.write_text("{not json at all")
    persistence.CONFIDENCE_FILE.write_text(json.dumps({"not": "a list"}))
    assert persistence.load_mistakes() == []
    assert persistence.load_confidence() == []
    # …and a later write repairs the file rather than raising
    persistence.log_mistake(persistence.mistake_entry_for(_q("a"), 0))
    assert [r["id"] for r in persistence.load_mistakes()] == ["a"]


def test_non_dict_rows_are_ignored(data_dir):
    data_dir.mkdir(parents=True)
    persistence.MISTAKES_FILE.write_text(json.dumps(["junk", 7, {"id": "a"}]))
    assert persistence.load_mistakes() == [{"id": "a"}]


# ------------------------------------------------------------ session journal
def _result() -> ExamResult:
    return ExamResult(mode="sprint", attempts=[
        ExamAttempt(_q("s1", "Sampler"), chosen_index=1),           # correct
        ExamAttempt(_q("s2", "Sampler"), chosen_index=3),           # miss
        ExamAttempt(_q("e1", "Estimator"), chosen_index=None),      # unanswered
    ], duration_secs=42.0)


def test_record_mistakes_logs_every_miss_with_a_null_cause(data_dir):
    logged = persistence.record_mistakes(_result())
    assert sorted(r["id"] for r in logged) == ["e1", "s2"]
    rows = persistence.load_mistakes()
    assert sorted(r["id"] for r in rows) == ["e1", "s2"]
    assert all(r["cause"] is None and r["resolved"] is False for r in rows)
    assert {r["id"]: r["your_answer"] for r in rows} == {
        "s2": "opt-d", "e1": "(no answer)"}


def test_record_mistakes_resolves_items_answered_correctly_this_time(data_dir):
    persistence.log_mistake(persistence.mistake_entry_for(_q("s1"), 0))
    persistence.update_mistake_cause("s1", "misread")
    persistence.record_mistakes(_result())       # s1 is correct in this session
    s1 = [r for r in persistence.load_mistakes() if r["id"] == "s1"]
    assert [r["resolved"] for r in s1] == [True]
    assert s1[0]["cause"] == "misread"


def test_record_mistakes_does_not_touch_exam_missed(data_dir):
    persistence.record_misses(_result())
    before = persistence.load_missed()
    persistence.record_mistakes(_result())
    assert persistence.load_missed() == before
    assert set(before[0]) == {"question_id", "section", "question",
                              "correct_answer", "chosen", "timestamp"}


def test_mistake_summary_counts_open_untagged_and_the_top_cause(data_dir):
    assert persistence.mistake_summary() == {
        "open": 0, "uncategorised": 0, "top_cause": None, "top_count": 0}
    for qid in ("a", "b", "c"):
        persistence.log_mistake(persistence.mistake_entry_for(_q(qid), 0))
    persistence.update_mistake_cause("a", "misread")
    persistence.update_mistake_cause("b", "misread")
    summary = persistence.mistake_summary()
    assert summary == {"open": 3, "uncategorised": 1,
                       "top_cause": "misread", "top_count": 2}
    persistence.resolve_mistake("a")
    assert persistence.mistake_summary()["open"] == 2


# -------------------------------------------------------------- confidence
def test_make_confidence_entry_schema_and_range():
    entry = persistence.make_confidence_entry("cc_depth", "Create circuits",
                                              4, False)
    assert set(entry) == CONFIDENCE_KEYS
    assert entry["app"] == "exam-sim"
    assert entry["confidence"] == 4 and entry["correct"] is False
    assert isinstance(entry["timestamp"], float)
    # The pure builder clamps, so a row that exists is always schema-valid…
    for bad, expected in ((0, 1), (5, 4), (-1, 1), (None, 1), ("3", 3)):
        assert persistence.make_confidence_entry(
            "x", "Sampler", bad, True)["confidence"] == expected


def test_log_confidence_rejects_a_rating_the_learner_never_gave(data_dir):
    """…but the *write* rejects rather than inventing one (common/README §3)."""
    for bad in (0, 5, -1, None, "high"):
        assert persistence.log_confidence("x", "Sampler", bad, True) is None
    assert persistence.load_confidence() == []
    assert not persistence.CONFIDENCE_FILE.exists()


def test_confidence_labels_cover_one_to_four():
    assert persistence.CONFIDENCE_LABELS == {
        1: "Guessing", 2: "Unsure", 3: "Fairly sure", 4: "Certain"}


def test_log_confidence_appends_pairings(data_dir):
    persistence.log_confidence("a", "Sampler", 4, False)
    persistence.log_confidence("b", "Estimator", 2, True)
    rows = json.loads(persistence.CONFIDENCE_FILE.read_text())
    assert [(r["id"], r["confidence"], r["correct"]) for r in rows] == [
        ("a", 4, False), ("b", 2, True)]


def test_record_confidence_logs_only_rated_attempts(data_dir):
    attempts = [
        ExamAttempt(_q("s1"), chosen_index=1, confidence=4),   # correct
        ExamAttempt(_q("s2"), chosen_index=3, confidence=1),   # miss
        ExamAttempt(_q("s3"), chosen_index=1),                 # not rated
    ]
    rows = persistence.record_confidence(ExamResult(mode="sprint",
                                                    attempts=attempts))
    assert [(r["id"], r["confidence"], r["correct"]) for r in rows] == [
        ("s1", 4, True), ("s2", 1, False)]
    assert persistence.load_confidence() == rows


def test_record_confidence_writes_nothing_when_nobody_rated(data_dir):
    persistence.record_confidence(_result())
    assert not persistence.CONFIDENCE_FILE.exists()


def test_confidence_file_is_capped(data_dir, monkeypatch):
    monkeypatch.setattr(journal, "CONFIDENCE_MAX", 4)
    for i in range(7):
        persistence.log_confidence(f"q{i}", "Sampler", 3, True)
    assert [r["id"] for r in persistence.load_confidence()] == [
        "q3", "q4", "q5", "q6"]


# ----------------------------------------------------------------- settings
def test_confidence_prompt_defaults_on_and_remembers_the_opt_out(data_dir):
    assert persistence.confidence_enabled() is True
    persistence.set_confidence_enabled(False)
    assert json.loads(persistence.SETTINGS_FILE.read_text()) == {
        "confidence_prompt": False}
    assert persistence.confidence_enabled() is False
    persistence.set_confidence_enabled(True)
    assert persistence.confidence_enabled() is True


def test_settings_tolerate_a_corrupt_file(data_dir):
    data_dir.mkdir(parents=True)
    persistence.SETTINGS_FILE.write_text("]not json[")
    assert persistence.load_settings() == persistence.DEFAULT_SETTINGS
    assert persistence.confidence_enabled() is True


def test_settings_keep_unknown_keys(data_dir):
    persistence.save_settings({"confidence_prompt": True, "future": 1})
    persistence.set_confidence_enabled(False)
    assert json.loads(persistence.SETTINGS_FILE.read_text()) == {
        "confidence_prompt": False, "future": 1}


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

    persistence.log_mistake(persistence.mistake_entry_for(_q("ours"), 0))
    persistence.update_mistake_cause("ours", "misread")
    persistence.resolve_mistake("ours")
    persistence.log_confidence("ours", "Sampler", 3, False)

    mistakes = json.loads((data_dir / "mistakes.json").read_text())
    assert mistakes[0] == FOREIGN_MISTAKE_ROW      # unchanged, unknown keys intact
    assert len(mistakes) > 1                       # and our own row was written
    assert {r["app"] for r in mistakes[1:]} == {"exam-sim"}
    confidence = json.loads((data_dir / "confidence.json").read_text())
    assert confidence[0] == FOREIGN_CONFIDENCE_ROW
    assert len(confidence) > 1
    assert {r["app"] for r in confidence[1:]} == {"exam-sim"}
