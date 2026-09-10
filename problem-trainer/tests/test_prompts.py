"""Prompt builders return (system, user) pairs carrying all grading context."""
import pytest

from ai.prompts import (GRADING_SYSTEM, STEP_SYSTEM, build_part_grading_prompt,
                        build_step_check_prompt)
from core.models import Derivation, Part, Problem, Step

PROBLEM = Problem(
    id="p_test", topic="Test Topic", title="Test Title", statement="STATEMENT-TEXT",
    parts=[Part(part_id="a", prompt="PART-PROMPT", points=4,
                rubric=["RUBRIC-ONE", "RUBRIC-TWO"], model_solution="MODEL-SOLUTION")],
)
DERIVATION = Derivation(
    id="deriv_test", title="Deriv Title", goal="DERIV-GOAL",
    steps=[
        Step(step_id="s1", prompt="S1-PROMPT", expected="S1-EXPECTED", hint="S1-HINT", model_step="S1-MODEL"),
        Step(step_id="s2", prompt="S2-PROMPT", expected="S2-EXPECTED", hint="S2-HINT", model_step="S2-MODEL"),
    ],
)


def test_part_grading_prompt_contains_all_context():
    system, user = build_part_grading_prompt(PROBLEM, PROBLEM.parts[0], "MY ANSWER", tries=2)
    assert system == GRADING_SYSTEM and system.strip()
    for needle in ("Test Title", "Test Topic", "STATEMENT-TEXT", "(a)", "4 points",
                   "PART-PROMPT", "- RUBRIC-ONE", "- RUBRIC-TWO", "MODEL-SOLUTION",
                   "MY ANSWER", "attempt #2"):
        assert needle in user, needle


def test_part_grading_prompt_requests_json_keys():
    _, user = build_part_grading_prompt(PROBLEM, PROBLEM.parts[0], "x")
    for key in ('"score"', '"feedback"', '"missed_points"'):
        assert key in user
    assert "JSON" in user


def test_part_grading_prompt_handles_empty_answer_and_clamps_tries():
    _, user = build_part_grading_prompt(PROBLEM, PROBLEM.parts[0], "   ", tries=0)
    assert "(empty)" in user
    assert "attempt #1" in user


def test_step_prompt_first_step_context():
    system, user = build_step_check_prompt(DERIVATION, DERIVATION.steps[0], "my step")
    assert system == STEP_SYSTEM and system.strip()
    assert "(this is the first step)" in user
    for needle in ("Deriv Title", "DERIV-GOAL", "(s1)", "S1-PROMPT", "S1-EXPECTED", "my step"):
        assert needle in user, needle
    assert "S1-HINT" not in user  # hints are for the student, not the grader


def test_step_prompt_lists_accepted_model_steps():
    _, user = build_step_check_prompt(DERIVATION, DERIVATION.steps[1], "ans",
                                      accepted_steps=[DERIVATION.steps[0]], tries=3)
    assert "1. S1-MODEL" in user
    assert "(this is the first step)" not in user
    assert "S2-EXPECTED" in user and "attempt #3" in user


def test_step_prompt_requests_json_keys():
    _, user = build_step_check_prompt(DERIVATION, DERIVATION.steps[0], "x")
    for key in ('"verdict"', '"nudge"', '"accept"', '"needs_work"'):
        assert key in user


def test_builders_work_for_every_bank_item(problems, derivations):
    for p in problems:
        for part in p.parts:
            system, user = build_part_grading_prompt(p, part, "answer")
            assert system and part.prompt in user and part.model_solution in user
    for d in derivations:
        for i, step in enumerate(d.steps):
            system, user = build_step_check_prompt(d, step, "answer", accepted_steps=d.steps[:i])
            assert system and step.prompt in user and step.expected in user
