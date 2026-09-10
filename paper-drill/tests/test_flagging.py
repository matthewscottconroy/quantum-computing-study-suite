"""Flag-for-review contract against a temp data dir.

Covers the shared suite contract for ``paper_flagged.json``: entry schema,
toggle semantics, stable ids, label truncation, and tolerance of malformed
files (coach.py --review globs every *_flagged.json, so this file must never
break it).
"""
import json
import re
import time

import pytest

import persistence
from config import APP_ID

FLAG_KEYS = {"id", "label", "category", "app", "timestamp"}


# ---------------------------------------------------------------------------
# Pure helpers
# ---------------------------------------------------------------------------

def test_make_flag_id_is_stable_and_well_formed():
    flag_id = persistence.make_flag_id("Paper", "What is a qubit?")
    assert re.fullmatch(r"paper-[0-9a-f]{16}", flag_id)
    assert flag_id == persistence.make_flag_id("Paper", "What is a qubit?")
    # surrounding whitespace is not part of the identity
    assert flag_id == persistence.make_flag_id("  Paper ", "What is a qubit? \n")
    # but the title and the question text both are
    assert flag_id != persistence.make_flag_id("Other Paper", "What is a qubit?")
    assert flag_id != persistence.make_flag_id("Paper", "What is a gate?")


def test_make_flag_label_collapses_whitespace_and_truncates():
    assert persistence.make_flag_label("short  question\n here") == "short question here"

    exact = "x" * persistence.FLAG_LABEL_MAX
    assert persistence.make_flag_label(exact) == exact

    long = "Why does the threshold theorem matter for the scheme? " * 4
    label = persistence.make_flag_label(long)
    assert persistence.FLAG_LABEL_MAX == 80
    assert len(label) <= 80
    assert label.endswith("…")
    assert "\n" not in label
    assert label[:-1] == label[:-1].rstrip()   # no dangling space before the ellipsis


# ---------------------------------------------------------------------------
# Toggle / unflag round-trips
# ---------------------------------------------------------------------------

def test_toggle_flag_writes_contract_entry(data_dir):
    flag_id = persistence.make_flag_id("Paper A", "Q1?")
    before = time.time()
    assert persistence.toggle_flag(flag_id, "Q1?", "Paper A") is True

    path = data_dir / "paper_flagged.json"
    assert persistence.FLAGGED_FILE == path
    assert path.exists()
    entries = json.loads(path.read_text())
    assert len(entries) == 1
    entry = entries[0]
    assert set(entry) == FLAG_KEYS
    assert entry["id"] == flag_id
    assert entry["label"] == "Q1?"
    assert entry["category"] == "Paper A"
    assert entry["app"] == APP_ID == "paper-drill"
    assert isinstance(entry["timestamp"], float)
    assert before <= entry["timestamp"] <= time.time() + 1
    assert persistence.is_flagged(flag_id)


def test_toggle_twice_removes_and_third_re_adds(data_dir):
    flag_id = persistence.make_flag_id("P", "Q")
    assert persistence.toggle_flag(flag_id, "Q", "P") is True
    assert persistence.toggle_flag(flag_id, "Q", "P") is False
    assert json.loads(persistence.FLAGGED_FILE.read_text()) == []
    assert not persistence.is_flagged(flag_id)
    assert persistence.toggle_flag(flag_id, "Q", "P") is True
    assert [e["id"] for e in persistence.load_flagged()] == [flag_id]


def test_flags_are_per_question(data_dir):
    q1 = persistence.make_flag_id("P", "Q1")
    q2 = persistence.make_flag_id("P", "Q2")
    persistence.toggle_flag(q1, "Q1", "P")
    persistence.toggle_flag(q2, "Q2", "P")
    assert [e["id"] for e in persistence.load_flagged()] == [q1, q2]
    persistence.unflag(q1)
    assert [e["id"] for e in persistence.load_flagged()] == [q2]
    assert persistence.is_flagged(q2) and not persistence.is_flagged(q1)


def test_unflag_unknown_id_is_a_noop(data_dir):
    assert persistence.load_flagged() == []
    persistence.unflag("paper-doesnotexist00")
    assert not persistence.FLAGGED_FILE.exists()   # nothing was written
    persistence.toggle_flag("paper-0000000000000001", "L", "C")
    persistence.unflag("paper-doesnotexist00")
    assert [e["id"] for e in persistence.load_flagged()] == ["paper-0000000000000001"]


# ---------------------------------------------------------------------------
# Robustness
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("raw,expected_ids", [
    ("{not json", []),
    (json.dumps({"id": "x"}), []),                       # not a list
    (json.dumps([{"label": "no id"}, 3, None, {"id": "ok", "label": "L"}]), ["ok"]),
    ("", []),
], ids=["corrupt", "non-list", "malformed-entries", "empty-file"])
def test_load_flagged_tolerates_bad_files(data_dir, raw, expected_ids):
    data_dir.mkdir(parents=True, exist_ok=True)
    persistence.FLAGGED_FILE.write_text(raw)
    assert [e["id"] for e in persistence.load_flagged()] == expected_ids
    assert not persistence.is_flagged("missing")


def test_toggle_recovers_from_corrupt_file(data_dir):
    data_dir.mkdir(parents=True, exist_ok=True)
    persistence.FLAGGED_FILE.write_text("{not json")
    assert persistence.toggle_flag("paper-00000000000000aa", "L", "C") is True
    entries = json.loads(persistence.FLAGGED_FILE.read_text())
    assert [e["id"] for e in entries] == ["paper-00000000000000aa"]


def test_missing_file_reads_as_empty(data_dir):
    assert not persistence.FLAGGED_FILE.exists()
    assert persistence.load_flagged() == []
    assert persistence.is_flagged("anything") is False
