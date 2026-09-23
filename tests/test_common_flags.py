"""``common.flags`` — the flag-for-review store.

Two things the ten copies got wrong in different combinations: five rewrote the
file from the *filtered* list (deleting rows they did not understand) and four
wrote it with ``write_text`` (truncate-then-write: a crash mid-write lost every
flag).  Both are asserted here, along with the legacy bare-id upgrade.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from common import flags, schema                    # noqa: E402

APP = "qec-trainer"


@pytest.fixture
def path(tmp_path):
    schema.reset_session()
    yield tmp_path / "qec_flagged.json"
    schema.reset_session()


# ---------------------------------------------------------------------------
# Labels and ids
# ---------------------------------------------------------------------------

def test_make_label_collapses_and_truncates():
    assert flags.make_label("  a\n b  ") == "a b"
    out = flags.make_label("x" * 200)
    assert len(out) == flags.LABEL_MAX and out.endswith("…")
    assert flags.make_label(None) == ""


def test_make_id_is_stable_across_whitespace():
    a = flags.make_id("Shor 1994", "What  is\nthe period?")
    b = flags.make_id("Shor  1994", "What is the period?")
    assert a == b
    assert a != flags.make_id("Shor 1994", "A different question?")
    assert flags.make_id("x", prefix="paper").startswith("paper-")


# ---------------------------------------------------------------------------
# Toggling
# ---------------------------------------------------------------------------

def test_toggle_flags_then_unflags(path):
    assert flags.toggle_flag(path, "q1", "A question", "Gates", app=APP) is True
    assert flags.is_flagged(path, "q1") is True
    rows = flags.load_flagged(path, APP)
    assert len(rows) == 1
    assert rows[0]["id"] == "q1"
    assert rows[0]["label"] == "A question"
    assert rows[0]["category"] == "Gates"
    assert rows[0]["app"] == APP
    assert rows[0]["timestamp"] > 0

    assert flags.toggle_flag(path, "q1", app=APP) is False
    assert flags.load_flagged(path, APP) == []


def test_flag_and_unflag_are_not_toggles(path):
    assert flags.flag(path, "q1", app=APP) is True
    assert flags.flag(path, "q1", app=APP) is False      # already flagged
    assert flags.unflag(path, "q1", app=APP) is True
    assert flags.unflag(path, "q1", app=APP) is False    # nothing to remove


def test_a_label_defaults_to_the_id(path):
    flags.flag(path, "q1", app=APP)
    assert flags.load_flagged(path, APP)[0]["label"] == "q1"


def test_flagged_ids(path):
    for i in range(3):
        flags.flag(path, f"q{i}", app=APP)
    assert flags.flagged_ids(path, APP) == {"q0", "q1", "q2"}


# ---------------------------------------------------------------------------
# Reading what is on disk
# ---------------------------------------------------------------------------

def test_missing_or_corrupt_file_reads_as_empty(path):
    assert flags.load_flagged(path, APP) == []
    assert flags.flagged_ids(path, APP) == set()
    path.write_text("{not json")
    assert flags.load_flagged(path, APP) == []
    path.write_text('{"an": "object"}')
    assert flags.load_flagged(path, APP) == []


def test_legacy_bare_id_file_is_read_and_upgraded(path):
    """flashcard-drill, qec-trainer and vqa-trainer wrote json.dumps(sorted(ids))."""
    path.write_text(json.dumps(["qec_steane", "qec_surface"]))
    rows = flags.load_flagged(path, APP)
    assert [r["id"] for r in rows] == ["qec_steane", "qec_surface"]
    assert all(r["app"] == APP and r["category"] == "" for r in rows)
    assert all(r["timestamp"] == 0.0 for r in rows), (
        "a bare id has no time; 0.0 keeps an old flag from jumping to the top "
        "of the review queue the day the file is rewritten")

    # The first write upgrades the file in place.
    flags.flag(path, "qec_new", "New", "Codes", app=APP)
    raw = json.loads(path.read_text())
    assert all(isinstance(r, dict) for r in raw)
    assert [r["id"] for r in raw] == ["qec_steane", "qec_surface", "qec_new"]


def test_is_flagged_works_on_a_legacy_file(path):
    path.write_text(json.dumps(["qec_steane"]))
    assert flags.is_flagged(path, "qec_steane") is True
    assert flags.toggle_flag(path, "qec_steane", app=APP) is False
    assert flags.load_flagged(path, APP) == []


def test_rows_with_alternative_id_keys_are_understood(path):
    path.write_text(json.dumps([{"problem_id": "p1"}, {"question_id": "q1"}]))
    assert {r["id"] for r in flags.load_flagged(path, APP)} == {"p1", "q1"}


def test_an_unusable_row_is_skipped_by_the_reader(path):
    path.write_text(json.dumps([{"no_id": True}, 42, None, {"id": "ok"}]))
    assert [r["id"] for r in flags.load_flagged(path, APP)] == ["ok"]


def test_a_foreign_apps_row_keeps_its_owner(path):
    path.write_text(json.dumps([{"id": "x", "app": "exam-sim", "label": "L",
                                 "category": "C", "timestamp": 5.0}]))
    flags.flag(path, "mine", app=APP)
    rows = {r["id"]: r for r in flags.load_flagged(path, APP)}
    assert rows["x"]["app"] == "exam-sim"
    assert rows["x"]["timestamp"] == 5.0
    assert rows["mine"]["app"] == APP


# ---------------------------------------------------------------------------
# Writing
# ---------------------------------------------------------------------------

def test_the_write_is_atomic_and_leaves_no_temp_file(path):
    flags.flag(path, "q1", app=APP)
    assert json.loads(path.read_text())
    assert not list(path.parent.glob("*.tmp"))


def test_the_file_is_version_stamped(path):
    flags.flag(path, "q1", app=APP)
    meta = schema.read_meta(path)
    assert meta["kind"] == "flagged" and meta["schema"] == 1


def test_a_newer_file_is_not_clobbered(path):
    flags.flag(path, "keep", app=APP)
    schema.sidecar_path(path).write_text(json.dumps({"schema": 99}))
    assert flags.flag(path, "new", app=APP) is True     # the toggle decided
    assert [r["id"] for r in flags.load_flagged(path, APP)] == ["keep"], (
        "the write should have been refused, leaving the newer file alone")


def test_save_flagged_normalises_a_mixed_list(path):
    assert flags.save_flagged(path, ["bare", {"id": "obj", "label": "L"}], APP)
    rows = json.loads(path.read_text())
    assert [r["id"] for r in rows] == ["bare", "obj"]
    assert all(set(r) == {"id", "label", "category", "app", "timestamp"}
               for r in rows)


def test_flagged_path_resolves_per_app(monkeypatch, tmp_path):
    monkeypatch.setenv("QUANTUM_STUDY_DATA_DIR", str(tmp_path))
    assert flags.flagged_path("qec-trainer") == tmp_path / "qec_flagged.json"
    assert flags.flagged_path("flashcard-drill") == tmp_path / "flagged_cards.json"


def test_coach_can_read_what_this_module_writes(path, monkeypatch, tmp_path):
    """The flagged files feed coach.py's review queue; its contract is
    {id, label, category, app, timestamp}."""
    import coach
    target = tmp_path / "qec_flagged.json"
    flags.flag(target, "qec_steane", "The Steane code", "Codes", app=APP)
    monkeypatch.setattr(coach, "DATA_DIR", tmp_path)
    rows = coach._load_list("qec_flagged.json")
    assert isinstance(rows, list) and len(rows) == 1
    assert set(rows[0]) == {"id", "label", "category", "app", "timestamp"}
