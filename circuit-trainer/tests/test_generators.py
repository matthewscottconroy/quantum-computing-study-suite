"""Every generator, at every difficulty, yields a well-formed, gradeable Problem."""
from __future__ import annotations

import random
from fractions import Fraction

import pytest

from core.models import AnswerFormat, Problem, ProblemCategory
from grading.auto_grader import grade
from problems import generate

CATEGORIES = list(ProblemCategory)
DIFFICULTIES = ("beginner", "intermediate", "advanced")
SAMPLES_PER_CELL = 3
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"

# Mirrors ui/screens/setup_screen.py: the deterministic, auto-graded categories
# that Sprint mode draws from. All of them must be MULTIPLE_CHOICE at every
# difficulty, or the sprint screen would block waiting on a Claude grade.
SPRINT_CATEGORIES = (
    ProblemCategory.MEASUREMENT_PROBS,
    ProblemCategory.SINGLE_GATE_OUTPUT,
    ProblemCategory.GATE_SEQUENCE,
    ProblemCategory.CIRCUIT_UNITARY,
    ProblemCategory.MULTI_QUBIT_OUTPUT,
)

# The only generators allowed to offer fewer than 4 options: the deliberately
# binary yes/no questions (entanglement-beginner, circuit equivalence).
BINARY_CATEGORIES = (ProblemCategory.ENTANGLEMENT, ProblemCategory.CIRCUIT_EQUIVALENCE)

# Generators that draw from a fixed pool and therefore stamp a stable problem_id
# (used for per-problem SRS weights and as the flag id).
DETERMINISTIC_ID_PREFIX = {
    ProblemCategory.GATE_SEQUENCE:    "gs:",
    ProblemCategory.NOTATION_READING: "notation:",
    ProblemCategory.GATE_IDENTITY:    "gi:",
}


@pytest.fixture(scope="module")
def samples() -> dict[tuple[ProblemCategory, str], list[Problem]]:
    random.seed(20260909)
    return {
        (cat, diff): [generate(cat, diff) for _ in range(SAMPLES_PER_CELL)]
        for cat in CATEGORIES
        for diff in DIFFICULTIES
    }


def _assert_valid(problem: Problem, category: ProblemCategory, difficulty: str) -> None:
    assert isinstance(problem, Problem)
    assert problem.category is category
    assert problem.difficulty == difficulty
    assert problem.question_text.strip()
    assert problem.solution_steps and all(isinstance(s, str) for s in problem.solution_steps)
    assert problem.key_concepts and all(isinstance(c, str) for c in problem.key_concepts)
    assert isinstance(problem.hints, list)
    for png in (problem.circuit_png, problem.aux_circuit_png):
        assert png is None or (isinstance(png, bytes) and png.startswith(PNG_MAGIC))

    fmt = problem.answer_format
    if fmt is AnswerFormat.MULTIPLE_CHOICE:
        assert problem.choices, "MC problem needs choices"
        assert all(isinstance(c, str) and c.strip() for c in problem.choices)
        idx = int(problem.correct_answer)
        assert 0 <= idx < len(problem.choices), (idx, problem.choices)
        # Every option distinct (so the keyed answer appears exactly once) and,
        # apart from the binary generators, always exactly four of them.
        assert len(set(problem.choices)) == len(problem.choices), (category, problem.choices)
        if category in BINARY_CATEGORIES:
            assert len(problem.choices) in (2, 4), (category, problem.choices)
        else:
            assert len(problem.choices) == 4, (category, problem.choices)
    elif fmt is AnswerFormat.NUMERIC:
        value = float(problem.correct_answer)
        assert value == value and abs(value) != float("inf")
    elif fmt is AnswerFormat.STATE_VECTOR:
        import ast
        import numpy as np

        vec = np.array(ast.literal_eval(str(problem.correct_answer)), dtype=complex)
        assert vec.ndim == 1 and len(vec) >= 2
        assert abs(np.linalg.norm(vec) - 1.0) < 1e-6
    elif fmt is AnswerFormat.FREE_FORM:
        assert not problem.choices
        # The rubric is what Claude grades against; it must exist.
        assert len(problem.solution_steps) >= 2
    else:  # pragma: no cover - enum is closed
        pytest.fail(f"unknown answer format {fmt}")


@pytest.mark.parametrize("category", CATEGORIES, ids=lambda c: c.name)
def test_generator_yields_valid_problem_at_every_difficulty(samples, category):
    for difficulty in DIFFICULTIES:
        for problem in samples[(category, difficulty)]:
            _assert_valid(problem, category, difficulty)


def test_only_circuit_explanation_is_free_form(samples):
    for (category, _), problems in samples.items():
        for p in problems:
            if category is ProblemCategory.CIRCUIT_EXPLANATION:
                assert p.answer_format is AnswerFormat.FREE_FORM
            else:
                assert p.answer_format is not AnswerFormat.FREE_FORM


def test_sprint_categories_are_multiple_choice_at_every_difficulty(samples):
    for category in SPRINT_CATEGORIES:
        for difficulty in DIFFICULTIES:
            for p in samples[(category, difficulty)]:
                assert p.answer_format is AnswerFormat.MULTIPLE_CHOICE, (category, difficulty)


def test_auto_grader_accepts_generated_answer_and_rejects_a_wrong_one(samples):
    checked = 0
    for (category, _), problems in samples.items():
        for p in problems:
            if p.answer_format is not AnswerFormat.MULTIPLE_CHOICE:
                continue
            idx = int(p.correct_answer)
            ok = grade(p, str(idx))
            assert ok.is_correct and ok.score == 10, (category, p.choices)
            wrong = (idx + 1) % len(p.choices)
            bad = grade(p, str(wrong))
            assert not bad.is_correct and bad.score == 0, (category, p.choices)
            checked += 1
    assert checked >= len(CATEGORIES) - 1


def _parse_prob(text: str) -> float:
    text = text.strip()
    if "/" in text:
        return float(Fraction(text))
    return float(text)


def test_measurement_correct_choice_is_a_probability(samples):
    for difficulty in DIFFICULTIES:
        for p in samples[(ProblemCategory.MEASUREMENT_PROBS, difficulty)]:
            value = _parse_prob(p.choices[int(p.correct_answer)])
            assert 0.0 <= value <= 1.0


def test_single_gate_correct_choice_is_a_genuine_gate_output():
    """The keyed answer must be the Dirac string of *some* catalogue gate applied
    to *some* catalogue input state - a semantic check that the MC key is real."""
    from qiskit import QuantumCircuit

    from problems._utils import (
        INPUT_STATES,
        SINGLE_QUBIT_GATES,
        format_statevector,
        statevector_for_circuit,
    )

    genuine: set[str] = set()
    for _, gate_fn in SINGLE_QUBIT_GATES.values():
        for sv in INPUT_STATES.values():
            qc = QuantumCircuit(1)
            gate_fn(qc, 0)
            genuine.add(format_statevector(statevector_for_circuit(qc, sv), 1))

    random.seed(11)
    for difficulty in DIFFICULTIES:
        for _ in range(6):
            p = generate(ProblemCategory.SINGLE_GATE_OUTPUT, difficulty)
            assert p.choices[int(p.correct_answer)] in genuine


def test_gate_identity_displayed_matrix_matches_keyed_gate():
    from problems._utils import GATE_MATRICES, render_matrix

    random.seed(5)
    for difficulty in DIFFICULTIES:
        for _ in range(6):
            p = generate(ProblemCategory.GATE_IDENTITY, difficulty)
            name = p.choices[int(p.correct_answer)]
            assert name in GATE_MATRICES
            body = render_matrix(GATE_MATRICES[name]).splitlines()
            assert p.matrix_str is not None
            for line in body:
                assert line in p.matrix_str


def test_deterministic_generators_stamp_stable_problem_ids(samples):
    for category, prefix in DETERMINISTIC_ID_PREFIX.items():
        for difficulty in DIFFICULTIES:
            for p in samples[(category, difficulty)]:
                assert p.problem_id and p.problem_id.startswith(prefix), (category, p.problem_id)


def test_notation_problem_id_is_one_to_one_with_the_question():
    random.seed(3)
    by_text: dict[str, set[str]] = {}
    by_id: dict[str, set[str]] = {}
    for difficulty in DIFFICULTIES:
        for _ in range(25):
            p = generate(ProblemCategory.NOTATION_READING, difficulty)
            by_text.setdefault(p.question_text, set()).add(p.problem_id)
            by_id.setdefault(p.problem_id, set()).add(p.question_text)
    assert all(len(ids) == 1 for ids in by_text.values())
    assert all(len(texts) == 1 for texts in by_id.values())
    assert len(by_id) >= 10


def test_random_generators_leave_problem_id_unset(samples):
    for difficulty in DIFFICULTIES:
        for p in samples[(ProblemCategory.SINGLE_GATE_OUTPUT, difficulty)]:
            assert p.problem_id is None


def test_unknown_category_raises():
    with pytest.raises((ValueError, AttributeError)):
        generate("not-a-category", "beginner")  # type: ignore[arg-type]
