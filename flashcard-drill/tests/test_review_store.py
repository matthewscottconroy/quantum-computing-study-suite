"""Unit tests for the mistake journal / confidence calibration store.

Pure Python, no Qt: everything here is the contract shape, the tolerance of a
missing or corrupt file, the atomic write and the per-app isolation of the two
suite-wide files.  The autouse ``data_dir`` fixture in ``conftest.py`` points
``QUANTUM_STUDY_DATA_DIR`` at a fresh directory, and every path is resolved
from it on each call, so nothing here can touch the real data directory.

Since the migration the store itself is :mod:`common.journal`, shared with the
other nine apps; ``persistence.review_store`` is the adapter that supplies this
app's identity, the timestamp-targeted ``set_mistake_cause`` the card screen
needs, and the settings file.  Three canonical behaviours differ from the old
local copy and are pinned here: a cause is case-normalised rather than
rejected, a note keeps its line breaks (and its own 500-character cap), and a
confidence rating outside 1-4 records nothing instead of being clamped.
"""
from __future__ import annotations

import json

import pytest

import common_path  # noqa: F401  (puts the repo root on sys.path)

import config
import persistence.review_store as rs
from common import journal

OTHER_APP = {
    "id": "q7", "app": "exam-sim", "category": "Complexity",
    "question": "BQP?", "your_answer": "P", "correct_answer": "bounded-error QP",
    "cause": "misread", "note": "", "timestamp": 10.0, "resolved": False,
}

MISTAKE_FIELDS = {"id", "app", "category", "question", "your_answer",
                  "correct_answer", "cause", "note", "timestamp", "resolved"}
CONFIDENCE_FIELDS = {"id", "app", "category", "confidence", "correct", "timestamp"}


# ---------------------------------------------------------------------------
# Paths / data-dir honouring
# ---------------------------------------------------------------------------

def test_paths_follow_the_relocated_data_dir(data_dir):
    assert rs.mistakes_path() == data_dir / "mistakes.json"
    assert rs.confidence_path() == data_dir / "confidence.json"
    assert rs.settings_path() == data_dir / "flashcard_settings.json"
    assert rs.mistakes_path() == config.mistakes_file()
    assert rs.mistakes_path() == journal.mistakes_path()


def test_everything_reads_empty_before_anything_is_written():
    assert not rs.mistakes_path().exists()
    assert rs.load_mistakes() == [] and rs.load_confidence() == []
    assert rs.cause_counts() == {} and rs.calibration_summary() == {}
    assert rs.confidently_wrong() == [] and rs.confidence_enabled() is True


# ---------------------------------------------------------------------------
# make_mistake_entry — the contract shape, without touching the disk
# ---------------------------------------------------------------------------

def test_make_mistake_entry_has_exactly_the_contract_fields():
    entry = rs.make_mistake_entry("pauli_xyx", "Pauli Matrices", "XYX = ?",
                                  "Self-rated: Missed", "-Y", timestamp=123.5)
    assert set(entry) == MISTAKE_FIELDS
    assert entry == {
        "id": "pauli_xyx", "app": "flashcard-drill", "category": "Pauli Matrices",
        "question": "XYX = ?", "your_answer": "Self-rated: Missed",
        "correct_answer": "-Y", "cause": None, "note": "",
        "timestamp": 123.5, "resolved": False,
    }
    assert isinstance(entry["timestamp"], float) and isinstance(entry["resolved"], bool)


@pytest.mark.parametrize("cause", rs.CAUSES)
def test_every_documented_cause_is_accepted(cause):
    assert rs.make_mistake_entry("c", cause=cause)["cause"] == cause


@pytest.mark.parametrize("bogus", ["typo", "", 3, None, "knew it, slipped"])
def test_an_unknown_cause_degrades_to_none(bogus):
    assert rs.make_mistake_entry("c", cause=bogus)["cause"] is None


@pytest.mark.parametrize("written", ["Misread", " misread ", "MISREAD"])
def test_a_recognisable_cause_is_normalised_rather_than_lost(written):
    """Canonical: case and surrounding space are forgiven (common/README §3)."""
    assert rs.make_mistake_entry("c", cause=written)["cause"] == "misread"


def test_long_multiline_text_is_collapsed_and_clipped_to_200_chars():
    entry = rs.make_mistake_entry(
        "c", question="line one\n\n   line two", correct_answer="x" * 500,
        note="n" * 400)
    assert entry["question"] == "line one line two"
    assert len(entry["correct_answer"]) == rs.MAX_TEXT
    assert entry["correct_answer"].endswith("…")


def test_the_note_keeps_its_line_breaks_and_has_its_own_cap():
    """Canonical: a one-line list field is collapsed; a typed note is not.

    Reflowing the note (as this copy used to) destroys structure the learner
    put there deliberately; it is capped at 500 instead.
    """
    entry = rs.make_mistake_entry("c", note="first line\nsecond line")
    assert entry["note"] == "first line\nsecond line"
    assert len(rs.make_mistake_entry("c", note="n" * 900)["note"]) == journal.NOTE_MAX


# ---------------------------------------------------------------------------
# Journal round trip
# ---------------------------------------------------------------------------

def test_log_load_categorise_and_resolve_round_trip():
    logged = rs.log_mistake("pauli_xyx", "Pauli Matrices", "XYX = ?",
                            "Self-rated: Missed", "-Y")
    assert logged is not None and logged["cause"] is None and logged["resolved"] is False

    on_disk = json.loads(rs.mistakes_path().read_text())
    assert isinstance(on_disk, list) and len(on_disk) == 1
    assert set(on_disk[0]) == MISTAKE_FIELDS

    assert rs.set_mistake_cause("pauli_xyx", "knew_but_slipped", note="sign again") is True
    entry = rs.load_mistakes(rs.APP_NAME)[0]
    assert (entry["cause"], entry["note"]) == ("knew_but_slipped", "sign again")

    assert rs.resolve_mistakes("pauli_xyx") == 1
    assert rs.load_mistakes()[0]["resolved"] is True
    assert rs.resolve_mistakes("pauli_xyx") == 0        # already closed


def test_set_mistake_cause_targets_one_entry_by_timestamp():
    first  = rs.log_mistake("c", timestamp=100.0)
    second = rs.log_mistake("c", timestamp=200.0)
    assert rs.set_mistake_cause("c", "misread", timestamp=first["timestamp"]) is True
    causes = {e["timestamp"]: e["cause"] for e in rs.load_mistakes()}
    assert causes == {100.0: "misread", 200.0: None}

    # Without a timestamp the newest entry is the one categorised.
    rs.set_mistake_cause("c", "out_of_time")
    causes = {e["timestamp"]: e["cause"] for e in rs.load_mistakes()}
    assert causes == {100.0: "misread", 200.0: "out_of_time"}
    assert second["timestamp"] == 200.0


def test_set_mistake_cause_on_an_unknown_card_is_a_no_op():
    assert rs.set_mistake_cause("never_logged", "misread") is False
    assert rs.load_mistakes() == []


def test_repeated_misses_are_separate_events_and_resolve_together():
    rs.log_mistake("c", timestamp=1.0)
    rs.log_mistake("c", timestamp=2.0)
    assert len(rs.load_mistakes()) == 2
    assert rs.resolve_mistakes("c") == 2
    assert all(e["resolved"] for e in rs.load_mistakes())


def test_cause_counts_buckets_uncategorised_separately():
    rs.log_mistake("a", cause="misread", timestamp=1.0)
    rs.log_mistake("b", cause="misread", timestamp=2.0)
    rs.log_mistake("c", timestamp=3.0)
    assert rs.cause_counts() == {"misread": 2, "uncategorised": 1}
    assert rs.cause_counts(since=2.5) == {"uncategorised": 1}


# ---------------------------------------------------------------------------
# Sharing the file with the rest of the suite
# ---------------------------------------------------------------------------

def test_another_apps_rows_survive_our_writes_and_our_filters():
    rs.mistakes_path().parent.mkdir(parents=True, exist_ok=True)
    rs.mistakes_path().write_text(json.dumps([OTHER_APP]))

    rs.log_mistake("mine")
    rs.set_mistake_cause("mine", "confused")
    rs.resolve_mistakes("mine")

    every = rs.load_mistakes()
    assert [e["app"] for e in every] == ["exam-sim", "flashcard-drill"]
    assert every[0] == OTHER_APP                         # byte-for-byte untouched
    assert [e["id"] for e in rs.load_mistakes(rs.APP_NAME)] == ["mine"]
    assert rs.cause_counts() == {"confused": 1}          # our app only, by default
    assert rs.cause_counts(app=None) == {"confused": 1, "misread": 1}


def test_resolve_and_cause_never_touch_another_apps_row_with_the_same_id():
    rs.mistakes_path().parent.mkdir(parents=True, exist_ok=True)
    rs.mistakes_path().write_text(json.dumps([dict(OTHER_APP, id="shared")]))
    assert rs.set_mistake_cause("shared", "other") is False
    assert rs.resolve_mistakes("shared") == 0
    assert rs.load_mistakes()[0]["cause"] == "misread"


# ---------------------------------------------------------------------------
# Corrupt / hostile files
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("junk", ["", "not json", "{}", "null", '{"a": 1}', "[1, 2, 3]"])
def test_a_corrupt_journal_reads_as_empty_and_is_repaired_by_the_next_write(junk):
    rs.mistakes_path().parent.mkdir(parents=True, exist_ok=True)
    rs.mistakes_path().write_text(junk)
    assert rs.load_mistakes() == []
    assert rs.log_mistake("c") is not None
    assert [e["id"] for e in rs.load_mistakes()] == ["c"]


def test_rows_without_a_usable_id_are_skipped_not_fatal():
    rs.mistakes_path().parent.mkdir(parents=True, exist_ok=True)
    rs.mistakes_path().write_text(json.dumps(
        [{"id": ""}, {"nope": 1}, "bare string", None, {"id": "  good  "}]))
    assert [e["id"] for e in rs.load_mistakes()] == ["good"]


def test_partial_rows_are_filled_in_with_contract_defaults():
    rs.mistakes_path().parent.mkdir(parents=True, exist_ok=True)
    rs.mistakes_path().write_text(json.dumps([{"id": "c", "timestamp": "oops"}]))
    entry = rs.load_mistakes()[0]
    assert set(entry) == MISTAKE_FIELDS
    assert entry["cause"] is None and entry["resolved"] is False
    assert entry["timestamp"] > 0


def test_an_unwritable_location_returns_none_instead_of_raising(monkeypatch, tmp_path):
    blocker = tmp_path / "not-a-dir"
    blocker.write_text("i am a file")
    monkeypatch.setenv("QUANTUM_STUDY_DATA_DIR", str(blocker / "nope"))
    assert rs.mistakes_path() == blocker / "nope" / "mistakes.json"
    assert rs.log_mistake("c") is None
    assert rs.log_confidence("c", "Cat", 3, True) is None
    assert rs.set_mistake_cause("c", "misread") is False
    assert rs.resolve_mistakes("c") == 0
    assert rs.save_settings({"confidence_prompt": False}) is False
    assert rs.load_mistakes() == [] and rs.load_confidence() == []


# ---------------------------------------------------------------------------
# Atomic write + growth cap
# ---------------------------------------------------------------------------

def test_the_write_is_atomic_and_leaves_no_temp_files(data_dir):
    rs.log_mistake("c")
    rs.log_confidence("c", "Cat", 2, False)
    leftovers = [p.name for p in data_dir.iterdir()
                 if p.name.startswith(".") or p.name.endswith(".tmp")]
    assert leftovers == []
    assert json.loads(rs.mistakes_path().read_text())      # valid JSON, non-empty


def test_the_caps_are_the_shared_ones():
    assert (rs.MISTAKE_LIMIT, rs.CONFIDENCE_LIMIT) == (journal.MISTAKES_MAX,
                                                       journal.CONFIDENCE_MAX)
    assert (rs.MISTAKE_LIMIT, rs.CONFIDENCE_LIMIT) == (2000, 5000)


def test_growth_is_capped_by_dropping_only_this_apps_oldest_rows(monkeypatch):
    """The cap is the file's, and only *our* rows are ever dropped to meet it.

    Eight of the ten apps used to sort the merged list and keep the newest N,
    which deleted other apps' rows during our own write.  ``trim_own`` never
    does: exam-sim's row below survives every one of our writes.
    """
    monkeypatch.setattr(journal, "MISTAKES_MAX", 4)
    monkeypatch.setattr(journal, "CONFIDENCE_MAX", 2)
    rs.mistakes_path().parent.mkdir(parents=True, exist_ok=True)
    rs.mistakes_path().write_text(json.dumps([OTHER_APP]))
    for i in range(6):
        rs.log_mistake(f"c{i}", timestamp=float(i))
        rs.log_confidence(f"c{i}", "Cat", 1, False, timestamp=float(i))
    every = rs.load_mistakes()
    assert len(every) == 4                                 # the file-wide cap
    assert every[0] == OTHER_APP                           # never ours to drop
    assert [e["id"] for e in rs.load_mistakes(rs.APP_NAME)] == ["c3", "c4", "c5"]
    assert [e["id"] for e in rs.load_confidence()] == ["c4", "c5"]


# ---------------------------------------------------------------------------
# Confidence calibration
# ---------------------------------------------------------------------------

def test_make_confidence_entry_has_exactly_the_contract_fields():
    entry = rs.make_confidence_entry("c", "Pauli Matrices", 3, True, timestamp=9.0)
    assert set(entry) == CONFIDENCE_FIELDS
    assert entry == {"id": "c", "app": "flashcard-drill", "category": "Pauli Matrices",
                     "confidence": 3, "correct": True, "timestamp": 9.0}
    assert isinstance(entry["correct"], bool)


@pytest.mark.parametrize("raw,clamped", [(0, 1), (-5, 1), (1, 1), (4, 4), (9, 4), ("2", 2)])
def test_confidence_is_clamped_into_1_to_4(raw, clamped):
    assert rs.make_confidence_entry("c", confidence=raw)["confidence"] == clamped


def test_confidence_log_load_and_calibration():
    rs.log_confidence("a", "Pauli Matrices", 4, False)     # confidently wrong
    rs.log_confidence("b", "Pauli Matrices", 4, True)
    rs.log_confidence("c", "Theorems", 1, True)            # a lucky guess
    assert [set(e) for e in rs.load_confidence()] == [CONFIDENCE_FIELDS] * 3
    # Canonical buckets: {"total", "correct"} (common/README §3), not {"n", …}.
    assert rs.calibration_summary() == {
        1: {"total": 1, "correct": 1},
        4: {"total": 2, "correct": 1},
    }
    assert [e["id"] for e in rs.confidently_wrong()] == ["a"]
    assert rs.confidently_wrong(threshold=5) == []


@pytest.mark.parametrize("bogus", [0, 5, -1, None, "high", True])
def test_an_out_of_range_rating_records_nothing_rather_than_being_clamped(bogus):
    """Canonical: clamping invents a rating the learner never gave."""
    assert rs.log_confidence("c", "Cat", bogus, True) is None
    assert rs.load_confidence() == []


def test_corrupt_confidence_rows_are_skipped():
    rs.confidence_path().parent.mkdir(parents=True, exist_ok=True)
    rs.confidence_path().write_text(json.dumps(
        [{"id": "a", "confidence": "high"}, {"confidence": 3}, {"id": "b", "confidence": 2}]))
    assert [e["id"] for e in rs.load_confidence()] == ["b"]


# ---------------------------------------------------------------------------
# Settings (the confidence opt-out)
# ---------------------------------------------------------------------------

def test_the_confidence_opt_out_persists_and_can_be_undone():
    assert rs.confidence_enabled() is True                 # default: ask
    assert rs.set_confidence_enabled(False) is True
    assert rs.confidence_enabled() is False
    assert json.loads(rs.settings_path().read_text()) == {"confidence_prompt": False}
    rs.set_confidence_enabled(True)
    assert rs.confidence_enabled() is True


def test_a_corrupt_settings_file_falls_back_to_the_default():
    rs.settings_path().parent.mkdir(parents=True, exist_ok=True)
    rs.settings_path().write_text("{oh no")
    assert rs.load_settings() == {"confidence_prompt": True}
    assert rs.confidence_enabled() is True


def test_unrelated_settings_keys_are_preserved():
    rs.settings_path().parent.mkdir(parents=True, exist_ok=True)
    rs.settings_path().write_text(json.dumps({"something_else": 7}))
    rs.set_confidence_enabled(False)
    assert json.loads(rs.settings_path().read_text()) == {
        "something_else": 7, "confidence_prompt": False}


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

    rs.log_mistake("ours", "Gates", "q", "a", "b")
    rs.set_mistake_cause("ours", "misread")
    rs.resolve_mistakes("ours")
    rs.log_confidence("ours", "Gates", 3, False)

    mistakes = json.loads((data_dir / "mistakes.json").read_text())
    assert mistakes[0] == FOREIGN_MISTAKE_ROW      # unchanged, unknown keys intact
    assert len(mistakes) > 1                       # and our own row was written
    assert {r["app"] for r in mistakes[1:]} == {"flashcard-drill"}
    confidence = json.loads((data_dir / "confidence.json").read_text())
    assert confidence[0] == FOREIGN_CONFIDENCE_ROW
    assert len(confidence) > 1
    assert {r["app"] for r in confidence[1:]} == {"flashcard-drill"}
