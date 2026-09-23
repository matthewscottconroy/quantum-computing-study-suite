"""History and flag persistence round-trip through a temp directory."""
from __future__ import annotations

import json
import math
import time

import pytest

import persistence
from core.models import Attempt, GradeMode, Problem, SessionStats, Verdict


def _problem(pid: str, cat: str = "Surface Code") -> Problem:
    return Problem(id=pid, category=cat, difficulty="intermediate", question="q",
                   choices=["a", "b"], correct_index=0, grade_mode=GradeMode.AUTO)


def _stats(rows: list[tuple[str, str, int, int]]) -> SessionStats:
    s = SessionStats()
    for pid, cat, score, hints in rows:
        v = Verdict.CORRECT if score >= 7 else Verdict.PARTIAL if score >= 4 else Verdict.INCORRECT
        s.attempts.append(Attempt(_problem(pid, cat), "A", score, v, "fb", hints_used=hints, elapsed_secs=9))
        s.total += 1
        s.correct += v is Verdict.CORRECT
    return s


def test_paths_are_isolated_and_empty(isolated_data_dir):
    assert persistence.HISTORY_FILE.is_relative_to(isolated_data_dir)
    assert persistence.FLAGGED_FILE.is_relative_to(isolated_data_dir)
    assert persistence._load_raw() == [] and persistence.load_flagged() == set()


def test_save_session_round_trip():
    persistence.save_session(_stats([("p1", "Surface Code", 10, 0), ("p2", "Steane Code", 0, 1)]))
    persistence.save_session(_stats([("p3", "Steane Code", 5, 0)]))
    raw = json.loads(persistence.HISTORY_FILE.read_text())
    assert raw == persistence._load_raw() and len(raw) == 2
    first = raw[0]
    assert first["total"] == 2 and first["correct"] == 1 and first["accuracy"] == 0.5
    assert abs(first["timestamp"] - time.time()) < 60
    assert first["attempts"][1] == {
        "problem_id": "p2", "category": "Steane Code", "difficulty": "intermediate",
        "score": 0, "verdict": "Incorrect", "hints_used": 1, "elapsed_secs": 9,
    }


def test_category_averages_and_problem_weights():
    persistence.save_session(_stats([
        ("mastered", "Surface Code", 10, 0),
        ("hinted", "Surface Code", 10, 2),     # effective score 9 -> 2 - 1.35
        ("missed", "Steane Code", 0, 0),
        ("half", "Steane Code", 5, 0),
    ]))
    avg = persistence.avg_scores_by_category()
    assert avg["Surface Code"] == pytest.approx(10.0)
    assert avg["Steane Code"] == pytest.approx(2.5)
    w = persistence.problem_score_weights()
    assert w["mastered"] == pytest.approx(0.5)
    assert w["hinted"] == pytest.approx(0.65)
    assert w["missed"] == pytest.approx(2.0)
    assert w["half"] == pytest.approx(1.25)
    assert "never-seen" not in w


def test_old_sessions_decay_with_14_day_half_life(isolated_data_dir):
    now = time.time()
    raw = [
        {"timestamp": now - 14 * 86400, "attempts": [{"problem_id": "p", "category": "C", "score": 0}]},
        {"timestamp": now, "attempts": [{"problem_id": "p", "category": "C", "score": 10}]},
        {"attempts": [{"problem_id": "legacy", "category": "L", "score": 10}]},   # no timestamp
    ]
    isolated_data_dir.mkdir(parents=True, exist_ok=True)
    persistence.HISTORY_FILE.write_text(json.dumps(raw))
    w_old = math.exp(-math.log(2))                       # 0.5
    expected = (w_old * 0 + 10) / (w_old + 1)
    assert persistence.avg_scores_by_category()["C"] == pytest.approx(expected, abs=1e-3)
    assert persistence.avg_scores_by_category()["L"] == pytest.approx(10.0)
    assert persistence._session_weight(raw[2]) == pytest.approx(0.1)


def test_flag_toggle_round_trip_and_corrupt_files(isolated_data_dir):
    assert persistence.toggle_flag("rep_distance", "What is the distance?",
                                   "Repetition Code") is True
    assert persistence.load_flagged() == {"rep_distance"}
    assert persistence.toggle_flag("stab_def") is True
    assert [e["id"] for e in persistence.flagged_entries()] == ["rep_distance", "stab_def"]
    assert persistence.toggle_flag("rep_distance") is False
    assert persistence.load_flagged() == {"stab_def"}

    persistence.FLAGGED_FILE.write_text("garbage")
    persistence.HISTORY_FILE.write_text("{nope")
    assert persistence.load_flagged() == set()
    assert persistence._load_raw() == []
    persistence.save_session(_stats([("p", "C", 10, 0)]))
    assert len(persistence._load_raw()) == 1


def test_a_flag_carries_the_question_so_coachs_review_queue_can_show_it():
    """The store used to hold bare ids, so the review queue listed "rep_distance"."""
    persistence.toggle_flag("rep_distance", "What is the distance of the "
                            "3-qubit repetition code?", "Repetition Code")
    entry, = persistence.flagged_entries()
    assert entry["id"] == "rep_distance"
    assert entry["label"].startswith("What is the distance")
    assert entry["category"] == "Repetition Code"
    assert entry["app"] == "qec-trainer"
    assert entry["timestamp"] > 0


def test_a_legacy_bare_id_flag_file_is_read_and_upgraded_in_place(isolated_data_dir):
    """Files written by the previous build must keep working, then improve."""
    isolated_data_dir.mkdir(parents=True, exist_ok=True)
    persistence.FLAGGED_FILE.write_text(json.dumps(["old_one", "old_two"]))

    assert persistence.load_flagged() == {"old_one", "old_two"}      # read as-is
    assert persistence.toggle_flag("new_one", "a new question", "Surface Code")

    rows = json.loads(persistence.FLAGGED_FILE.read_text())
    assert [r["id"] for r in rows] == ["old_one", "old_two", "new_one"]
    assert rows[0] == {"id": "old_one", "label": "old_one", "category": "",
                       "app": "qec-trainer", "timestamp": 0.0}
    assert rows[2]["label"] == "a new question"
    assert persistence.load_flagged() == {"old_one", "old_two", "new_one"}


def test_an_unparseable_flag_row_is_kept_not_deleted(isolated_data_dir):
    """A rewrite must not delete rows this build does not understand."""
    isolated_data_dir.mkdir(parents=True, exist_ok=True)
    persistence.FLAGGED_FILE.write_text(json.dumps(
        [{"id": "keep", "label": "l", "unknown_key": [1, 2]}, "bare"]))
    persistence.toggle_flag("added")
    rows = json.loads(persistence.FLAGGED_FILE.read_text())
    assert [r["id"] for r in rows] == ["keep", "bare", "added"]


def test_history_survives_a_refused_write_and_says_so(isolated_data_dir):
    """A file written by a newer build is never overwritten by this one."""
    from common import schema

    persistence.save_session(_stats([("p1", "C", 10, 0)]))
    before = persistence.HISTORY_FILE.read_text()
    schema.sidecar_path(persistence.HISTORY_FILE).write_text(json.dumps(
        {"file": "qec_history.json", "kind": "history", "schema": 42}))

    persistence.clear_write_error()
    assert persistence.save_session(_stats([("p2", "C", 0, 0)])) is False
    assert persistence.HISTORY_FILE.read_text() == before
    assert isinstance(persistence.last_write_error(), schema.SchemaTooNewError)
    persistence.clear_write_error()
