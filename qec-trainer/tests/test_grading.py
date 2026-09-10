"""Auto-grader, problem-set builder, and Claude prompt template (no API calls)."""
from __future__ import annotations

import random

import pytest

from core.models import GradeMode, Problem, TrainerConfig, Verdict
from grading.auto_grader import grade_mc
from problems import all_problems, build_problem_set


def _mc() -> Problem:
    return Problem(id="t1", category="Repetition Code", difficulty="beginner",
                   question="q?", choices=["w", "x", "RIGHT", "z"], correct_index=2,
                   explanation="because", grade_mode=GradeMode.AUTO)


def test_grade_mc_accepts_correct_letter_case_insensitively():
    for ans in ("C", "c", " c "):
        a = grade_mc(_mc(), ans)
        assert a.verdict is Verdict.CORRECT and a.score == 10
        assert a.model_answer == "RIGHT" and "because" in a.feedback


def test_grade_mc_rejects_wrong_or_invalid():
    for ans in ("A", "D", "E", "", "2"):
        a = grade_mc(_mc(), ans)
        assert a.verdict is Verdict.INCORRECT and a.score == 0
        assert "C: RIGHT" in a.feedback


def test_build_problem_set_filters_by_category_and_difficulty():
    random.seed(0)
    bank = all_problems()
    cat = "Steane Code"
    picked = build_problem_set(TrainerConfig(categories=[cat], difficulty=None, problem_count=8))
    assert len(picked) == 8
    assert all(p.category == cat for p in picked)
    assert len({p.id for p in picked}) == 8

    beginners = build_problem_set(TrainerConfig(categories=[cat], difficulty="beginner", problem_count=3))
    assert 1 <= len(beginners) <= 3 and all(p.difficulty == "beginner" for p in beginners)

    pool = [p for p in bank if p.category == cat]
    everything = build_problem_set(TrainerConfig(categories=[cat], difficulty=None, problem_count=10_000))
    assert sorted(p.id for p in everything) == sorted(p.id for p in pool)

    assert build_problem_set(TrainerConfig(categories=[], difficulty=None, problem_count=5)) == []


def test_build_problem_set_flagged_only_uses_persisted_flags():
    import persistence

    ids = [p.id for p in all_problems()[:3]]
    persistence.save_flagged(set(ids))
    picked = build_problem_set(TrainerConfig(categories=[], difficulty=None, problem_count=10, flagged_only=True))
    assert sorted(p.id for p in picked) == sorted(ids)


def test_claude_prompt_template_and_missing_key(tmp_path, monkeypatch):
    from grading import claude_grader
    import config

    assert config.MODEL == "claude-sonnet-4-6"
    prompt = claude_grader._TMPL.format(question="Q_TXT", model_answer="REF_TXT", student_answer="STU_TXT")
    for token in ("Q_TXT", "REF_TXT", "STU_TXT", '"score"', '"feedback"', '"model_answer"'):
        assert token in prompt
    assert claude_grader._SYSTEM.strip()

    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setattr(claude_grader, "API_KEY_FILE", tmp_path / "nope.txt")
    with pytest.raises(RuntimeError, match="API key"):
        claude_grader._get_client()
    with pytest.raises(RuntimeError):
        claude_grader.grade_open(_mc(), "anything")
