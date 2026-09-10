"""Exam logistics helpers, the data-dir override, and the ExamAttempt / ExamResult models."""
import os
import subprocess
import sys
from pathlib import Path

import pytest

from config import (EXAM_MINUTES, EXAM_QUESTION_COUNT, PASS_MARK, SECTIONS,
                    SPRINT_MINUTES, SPRINT_QUESTION_COUNT, pass_mark_for,
                    section_weight)
from core.models import ExamAttempt, ExamResult, Question


def _q(qid: str, section: str = "Sampler", correct: int = 1) -> Question:
    return Question(id=qid, section=section, question="q?",
                    options=["a", "b", "c", "d"], correct_index=correct,
                    explanation="because", difficulty="easy")


def test_exam_logistics_constants():
    assert (EXAM_QUESTION_COUNT, EXAM_MINUTES, PASS_MARK) == (68, 90, 47)
    assert (SPRINT_QUESTION_COUNT, SPRINT_MINUTES) == (10, 10)


def test_section_weights_sum_to_one():
    assert sum(section_weight(s) for s in SECTIONS) == pytest.approx(1.0)
    assert section_weight("Nope") == 0.0


def test_pass_mark_scales_with_session_size():
    assert pass_mark_for(68) == 47                      # the real exam
    for total, expected in ((10, 7), (34, 24), (110, 77), (1, 1)):
        assert pass_mark_for(total) == expected, total  # ceil(total * 47 / 68)


def test_attempt_answered_and_correct():
    attempt = ExamAttempt(_q("x"))
    assert attempt.answered is False and attempt.correct is False
    attempt.chosen_index = 1
    assert attempt.answered and attempt.correct
    attempt.chosen_index = 0
    assert attempt.answered and not attempt.correct


def test_result_counts_missed_and_section_breakdown():
    result = ExamResult(mode="full", attempts=[
        ExamAttempt(_q("s1", "Sampler"), chosen_index=1),
        ExamAttempt(_q("s2", "Sampler"), chosen_index=0),
        ExamAttempt(_q("e1", "Estimator"), chosen_index=None),
    ], duration_secs=12.5)
    assert (result.total, result.correct) == (3, 1)
    assert [a.question.id for a in result.missed] == ["s2", "e1"]
    assert result.section_breakdown() == {
        "Sampler": {"total": 2, "correct": 1},
        "Estimator": {"total": 1, "correct": 0},
    }


def _config_paths(env_override: str | None) -> list[str]:
    """DATA_DIR / HISTORY_FILE / MISSED_FILE as a fresh interpreter resolves them."""
    env = {k: v for k, v in os.environ.items() if k != "QUANTUM_STUDY_DATA_DIR"}
    if env_override is not None:
        env["QUANTUM_STUDY_DATA_DIR"] = env_override
    out = subprocess.run(
        [sys.executable, "-c",
         "import config; print(config.DATA_DIR); print(config.HISTORY_FILE); print(config.MISSED_FILE)"],
        cwd=Path(__file__).resolve().parent.parent, env=env, capture_output=True, text=True,
        check=True, timeout=60)
    return out.stdout.strip().splitlines()


def test_data_dir_honours_quantum_study_data_dir(tmp_path):
    override = tmp_path / "suite-data"
    data_dir, history, missed = _config_paths(str(override))
    assert Path(data_dir) == override
    assert Path(history) == override / "exam_history.json"
    assert Path(missed) == override / "exam_missed.json"


def test_data_dir_defaults_to_the_shared_suite_directory():
    data_dir, history, _ = _config_paths(None)
    assert Path(data_dir) == Path.home() / ".local" / "share" / "quantum-study"
    assert Path(history).name == "exam_history.json"
