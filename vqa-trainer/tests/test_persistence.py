"""History and flag persistence round-trip through a temp directory."""
from __future__ import annotations

import json
import math
import time

import pytest

import persistence
from core.models import Attempt, GradeMode, Problem, SessionStats, Verdict


def _problem(pid: str, cat: str = "QAOA") -> Problem:
    return Problem(id=pid, category=cat, difficulty="intermediate", question="q",
                   choices=["a", "b"], correct_index=0, grade_mode=GradeMode.MC)


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
    assert persistence._load_raw() == [] and persistence.load_flagged() == set()


def test_save_session_round_trip():
    persistence.save_session(_stats([("p1", "QAOA", 10, 0), ("p2", "Barren Plateaus", 0, 1)]))
    persistence.save_session(_stats([("p3", "Barren Plateaus", 5, 0)]))
    raw = json.loads(persistence.HISTORY_FILE.read_text())
    assert raw == persistence._load_raw() and len(raw) == 2
    first = raw[0]
    assert first["total"] == 2 and first["correct"] == 1 and first["accuracy"] == 0.5
    assert abs(first["timestamp"] - time.time()) < 60
    assert first["attempts"][1] == {
        "problem_id": "p2", "category": "Barren Plateaus", "difficulty": "intermediate",
        "score": 0, "verdict": "Incorrect", "hints_used": 1, "elapsed_secs": 9,
    }


def test_category_averages_and_problem_weights():
    persistence.save_session(_stats([
        ("mastered", "QAOA", 10, 0),
        ("hinted", "QAOA", 10, 2),          # effective score 9 -> 2 - 1.35
        ("missed", "Ansatz Design", 0, 0),
        ("half", "Ansatz Design", 5, 0),
    ]))
    avg = persistence.avg_scores_by_category()
    assert avg["QAOA"] == pytest.approx(10.0)
    assert avg["Ansatz Design"] == pytest.approx(2.5)
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
    assert persistence.toggle_flag("qaoa_structure") is True
    assert persistence.load_flagged() == {"qaoa_structure"}
    assert persistence.toggle_flag("bp_definition") is True
    assert json.loads(persistence._FLAGGED_FILE.read_text()) == ["bp_definition", "qaoa_structure"]
    assert persistence.toggle_flag("qaoa_structure") is False
    assert persistence.load_flagged() == {"bp_definition"}

    persistence._FLAGGED_FILE.write_text("garbage")
    persistence.HISTORY_FILE.write_text("{nope")
    assert persistence.load_flagged() == set()
    assert persistence._load_raw() == []
    persistence.save_session(_stats([("p", "C", 10, 0)]))
    assert len(persistence._load_raw()) == 1
