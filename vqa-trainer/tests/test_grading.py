"""MC and numeric auto-graders, problem-set builder, Claude prompt template (no API)."""
from __future__ import annotations

import random

import pytest

from core.models import GradeMode, Problem, TrainerConfig, Verdict
from grading.auto_grader import grade_mc, grade_numeric
from problems import all_problems, build_problem_set


def _mc() -> Problem:
    return Problem(id="t1", category="QAOA", difficulty="beginner", question="q?",
                   choices=["w", "RIGHT", "y", "z"], correct_index=1,
                   explanation="because", grade_mode=GradeMode.MC)


def _numeric(value=0.4, tol=1e-4) -> Problem:
    return Problem(id="n1", category="Parameter Shift", difficulty="intermediate",
                   question="compute", correct_value=value, tolerance=tol,
                   explanation="shift rule", grade_mode=GradeMode.AUTO)


def test_grade_mc_accepts_correct_and_rejects_wrong():
    for ans in ("B", "b", " b "):
        a = grade_mc(_mc(), ans)
        assert a.verdict is Verdict.CORRECT and a.score == 10 and a.model_answer == "RIGHT"
    for ans in ("A", "D", "Z", ""):
        a = grade_mc(_mc(), ans)
        assert a.verdict is Verdict.INCORRECT and a.score == 0
        assert "B: RIGHT" in a.feedback


def test_grade_numeric_exact_within_tolerance():
    p = _numeric()
    for ans in ("0.4", "0.40005", " .4 ", "0,4"):
        a = grade_numeric(p, ans)
        assert a.verdict is Verdict.CORRECT and a.score == 10, ans
    assert grade_numeric(p, "0.4").model_answer == "0.4"


def test_grade_numeric_partial_band_and_incorrect():
    p = _numeric(value=1.0, tol=0.01)
    near = grade_numeric(p, "1.1")            # diff 0.1 = 10*tol -> partial
    assert near.verdict is Verdict.PARTIAL and 4 <= near.score < 10
    nearer = grade_numeric(p, "1.02")
    assert nearer.verdict is Verdict.PARTIAL and nearer.score >= near.score
    far = grade_numeric(p, "2.0")
    assert far.verdict is Verdict.INCORRECT and far.score == 0
    junk = grade_numeric(p, "about one")
    assert junk.verdict is Verdict.INCORRECT and junk.score == 0
    assert "parse" in junk.feedback.lower()


def test_bank_numeric_problems_grade_their_own_key():
    for p in all_problems():
        if p.grade_mode is GradeMode.AUTO:
            assert grade_numeric(p, repr(p.correct_value)).verdict is Verdict.CORRECT, p.id
            assert grade_numeric(p, repr(p.correct_value + 1.0)).verdict is Verdict.INCORRECT, p.id
        elif p.grade_mode is GradeMode.MC:
            assert grade_mc(p, chr(65 + p.correct_index)).verdict is Verdict.CORRECT, p.id


def test_build_problem_set_filters_and_flagged_only():
    import persistence

    random.seed(0)
    bank = all_problems()
    cat = "QAOA"
    picked = build_problem_set(TrainerConfig(categories=[cat], difficulty=None, problem_count=6))
    assert len(picked) == 6 and len({p.id for p in picked}) == 6
    assert all(p.category == cat for p in picked)

    adv = build_problem_set(TrainerConfig(categories=[cat], difficulty="advanced", problem_count=4))
    assert 1 <= len(adv) <= 4 and all(p.difficulty == "advanced" for p in adv)

    pool = [p for p in bank if p.category == cat]
    everything = build_problem_set(TrainerConfig(categories=[cat], difficulty=None, problem_count=10_000))
    assert sorted(p.id for p in everything) == sorted(p.id for p in pool)
    assert build_problem_set(TrainerConfig(categories=[], difficulty=None, problem_count=5)) == []

    ids = [p.id for p in bank[:3]]
    persistence.save_flagged(set(ids))
    flagged = build_problem_set(TrainerConfig(categories=[], difficulty=None, problem_count=10, flagged_only=True))
    assert sorted(p.id for p in flagged) == sorted(ids)


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
