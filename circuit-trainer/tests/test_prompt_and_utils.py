"""Claude prompt builder is well-formed (no API call) and shared helpers behave."""
from __future__ import annotations

import math

import numpy as np
import pytest

from config import CLAUDE_MODEL
from core.models import AnswerFormat, Problem, ProblemCategory


def _explanation_problem() -> Problem:
    return Problem(
        category=ProblemCategory.CIRCUIT_EXPLANATION, difficulty="intermediate",
        question_text="What does H-CNOT do to |00>?",
        answer_format=AnswerFormat.FREE_FORM, correct_answer="",
        choices=None, circuit_png=None, aux_circuit_png=None,
        matrix_str=None, state_str=None,
        solution_steps=["H makes |+>|0>", "CNOT entangles -> Bell state"],
        key_concepts=["Bell state", "entanglement"],
    )


def test_prompt_builder_embeds_question_rubric_answer_and_schema():
    from grading import claude_grader

    p = _explanation_problem()
    prompt = claude_grader._build_prompt(p, "STUDENT_TEXT_42")
    assert p.question_text in prompt
    assert "STUDENT_TEXT_42" in prompt
    for step in p.solution_steps:
        assert step in prompt
    assert "Bell state, entanglement" in prompt
    assert p.category.value in prompt and "intermediate" in prompt
    for key in ('"score"', '"feedback"', '"model_answer"', '"follow_up"'):
        assert key in prompt
    assert CLAUDE_MODEL == "claude-sonnet-4-6"


def test_free_form_grader_raises_cleanly_without_api_key(tmp_path, monkeypatch):
    from grading import claude_grader

    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setattr(claude_grader, "API_KEY_FILE", tmp_path / "missing_key.txt")
    with pytest.raises(claude_grader.GradingError, match="API key"):
        claude_grader.grade_free_form(_explanation_problem(), "answer")


def test_formatting_helpers_recognise_symbolic_values():
    from qiskit.quantum_info import Statevector

    from problems._utils import GATE_MATRICES, format_statevector, render_matrix

    h = render_matrix(GATE_MATRICES["H"], label="Matrix M:")
    assert h.startswith("Matrix M:")
    assert "1/√2" in h and "−1/√2" in h
    assert "e^(iπ/4)" in render_matrix(GATE_MATRICES["T"])
    y = render_matrix(np.array([[0, -1j], [1j, 0]]))
    assert "−i" in y and " i" in y

    assert format_statevector(Statevector([1, 0]), 1) == "|0⟩"
    assert format_statevector(Statevector([0, -1]), 1) == "−|1⟩"
    s = 1 / math.sqrt(2)
    assert format_statevector(Statevector([s, 0, 0, s]), 2) == "(1/√2)|00⟩ + (1/√2)|11⟩"
    assert format_statevector(Statevector([s, -s]), 1) == "(1/√2)|0⟩ − (1/√2)|1⟩"


def test_distractor_helpers_never_return_the_correct_answer():
    from problems._utils import make_distractors, make_prob_distractors

    correct = "(1/√2)|00⟩ + (1/√2)|11⟩"
    for _ in range(20):
        d = make_distractors(correct, 3)
        assert len(d) == 3 and correct not in d and len(set(d)) == 3

    for correct_p in (0.0, 0.25, 0.5, 0.853553, 1.0):
        d = make_prob_distractors(correct_p, 3)
        assert 1 <= len(d) <= 3
        assert all(0.0 <= v <= 1.0 for v in d)
        assert all(abs(v - correct_p) > 1e-3 for v in d)
        assert len(set(d)) == len(d)

