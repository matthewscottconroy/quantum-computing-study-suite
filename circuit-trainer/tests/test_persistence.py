"""Session history round-trips through a temp dir; SRS weights follow the documented formula."""
from __future__ import annotations

import datetime
import json
import math
import os
import pathlib
import subprocess
import sys

import pytest

import persistence
from core.models import AnswerFormat, Attempt, Problem, ProblemCategory, SessionStats


def _problem(cat: ProblemCategory, pid: str | None = None, difficulty="beginner") -> Problem:
    return Problem(
        category=cat, difficulty=difficulty, question_text="q",
        answer_format=AnswerFormat.MULTIPLE_CHOICE, correct_answer="0",
        choices=["a", "b"], circuit_png=None, aux_circuit_png=None,
        matrix_str=None, state_str=None, solution_steps=["s"],
        key_concepts=["k"], problem_id=pid,
    )


def _stats(rows: list[tuple[ProblemCategory, str | None, int]]) -> SessionStats:
    stats = SessionStats()
    for cat, pid, score in rows:
        p = _problem(cat, pid)
        ok = score >= 7
        stats.attempts.append(Attempt(p, "0", ok, score, "fb", elapsed_secs=12))
        stats.total += 1
        if ok:
            stats.correct += 1
        elif score >= 4:
            stats.partial += 1
        else:
            stats.wrong += 1
    return stats


def test_save_session_round_trip(isolated_data_dir):
    assert persistence._HISTORY_FILE.is_relative_to(isolated_data_dir)
    assert not persistence._HISTORY_FILE.exists() and persistence._load_raw() == []

    stats = _stats([
        (ProblemCategory.SINGLE_GATE_OUTPUT, "sg-1", 10),
        (ProblemCategory.GATE_SEQUENCE, "gs-1", 0),
    ])
    persistence.save_session(stats)
    persistence.save_session(_stats([(ProblemCategory.NOISE_CHANNEL, None, 5)]), sprint=True)

    assert persistence._HISTORY_FILE.exists()
    raw = json.loads(persistence._HISTORY_FILE.read_text())
    assert raw == persistence._load_raw()
    assert len(raw) == 2

    first, second = raw
    assert first["total"] == 2 and first["correct"] == 1 and first["accuracy"] == 0.5
    assert "sprint" not in first and second["sprint"] is True
    assert datetime.datetime.fromisoformat(first["timestamp"]).tzinfo is not None
    a0 = first["attempts"][0]
    assert a0 == {
        "problem_id": "sg-1",
        "category": ProblemCategory.SINGLE_GATE_OUTPUT.value,
        "difficulty": "beginner",
        "score": 10,
        "elapsed_secs": 12,
    }


def test_avg_scores_by_category_is_a_per_category_mean():
    persistence.save_session(_stats([
        (ProblemCategory.SINGLE_GATE_OUTPUT, None, 10),
        (ProblemCategory.SINGLE_GATE_OUTPUT, None, 4),
        (ProblemCategory.GATE_SEQUENCE, None, 0),
    ]))
    avg = persistence.avg_scores_by_category()
    assert avg[ProblemCategory.SINGLE_GATE_OUTPUT.value] == pytest.approx(7.0)
    assert avg[ProblemCategory.GATE_SEQUENCE.value] == pytest.approx(0.0)
    assert ProblemCategory.NOISE_CHANNEL.value not in avg


def test_problem_score_weights_follow_documented_formula():
    persistence.save_session(_stats([
        (ProblemCategory.SINGLE_GATE_OUTPUT, "mastered", 10),
        (ProblemCategory.SINGLE_GATE_OUTPUT, "missed", 0),
        (ProblemCategory.SINGLE_GATE_OUTPUT, "half", 5),
        (ProblemCategory.SINGLE_GATE_OUTPUT, None, 0),   # no id -> ignored
    ]))
    w = persistence.problem_score_weights()
    assert w["mastered"] == pytest.approx(0.5)          # max(0.5, 2 - 1.5)
    assert w["missed"] == pytest.approx(2.0)
    assert w["half"] == pytest.approx(1.25)
    assert "unseen" not in w and None not in w


def test_time_decay_halves_weight_every_14_days(isolated_data_dir):
    today = datetime.date.today()
    old_day = today - datetime.timedelta(days=14)
    raw = [
        {"date": str(old_day), "attempts": [{"problem_id": "p", "category": "C", "score": 0}]},
        {"date": str(today), "attempts": [{"problem_id": "p", "category": "C", "score": 10}]},
    ]
    isolated_data_dir.mkdir(parents=True, exist_ok=True)
    persistence._HISTORY_FILE.write_text(json.dumps(raw))

    w_old = math.exp(-14 * math.log(2) / 14.0)          # 0.5
    expected_avg = (w_old * 0 + 1.0 * 10) / (w_old + 1.0)
    assert persistence.avg_scores_by_category()["C"] == pytest.approx(expected_avg, abs=1e-3)
    assert persistence.problem_score_weights()["p"] == pytest.approx(
        max(0.5, 2.0 - expected_avg * 0.15), abs=1e-3)


def test_corrupt_history_is_treated_as_empty_and_recoverable(isolated_data_dir):
    isolated_data_dir.mkdir(parents=True, exist_ok=True)
    persistence._HISTORY_FILE.write_text("{not json")
    assert persistence._load_raw() == []
    assert persistence.avg_scores_by_category() == {}
    persistence.save_session(_stats([(ProblemCategory.GATE_SEQUENCE, "x", 10)]))
    assert len(persistence._load_raw()) == 1


# ── QUANTUM_STUDY_DATA_DIR ────────────────────────────────────────────────────
# The override is read at import time, so check it from a fresh interpreter
# (the autouse fixture patches the constants in-process for isolation).

_APP_ROOT = pathlib.Path(persistence.__file__).resolve().parent
_PRINT_PATHS = (
    "import json, persistence; print(json.dumps([str(persistence._DATA_DIR), "
    "str(persistence._HISTORY_FILE), str(persistence.flagged_file())]))"
)


def _paths_in_fresh_interpreter(env: dict) -> list[str]:
    out = subprocess.run([sys.executable, "-c", _PRINT_PATHS], cwd=_APP_ROOT, env=env,
                         capture_output=True, text=True, check=True, timeout=120).stdout
    return json.loads(out)


def test_quantum_study_data_dir_env_var_redirects_both_files(tmp_path):
    target = tmp_path / "redirected"
    env = {**os.environ, "QUANTUM_STUDY_DATA_DIR": str(target)}
    data_dir, history, flagged = _paths_in_fresh_interpreter(env)
    assert data_dir == str(target)
    assert history == str(target / "trainer_history.json")
    assert flagged == str(target / "trainer_flagged.json")


def test_default_data_dir_when_env_var_unset():
    env = {k: v for k, v in os.environ.items() if k != "QUANTUM_STUDY_DATA_DIR"}
    data_dir, history, flagged = _paths_in_fresh_interpreter(env)
    expected = pathlib.Path.home() / ".local" / "share" / "quantum-study"
    assert data_dir == str(expected)
    assert history == str(expected / "trainer_history.json")
    assert flagged == str(expected / "trainer_flagged.json")
