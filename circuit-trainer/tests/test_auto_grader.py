"""Local grader: MC, numeric tolerance, and global-phase-invariant state vectors."""
from __future__ import annotations

import cmath
import math

from config import NUMERIC_TOLERANCE
from core.models import AnswerFormat, Attempt, Problem, ProblemCategory
from grading.auto_grader import grade


def _problem(fmt: AnswerFormat, correct, choices=None) -> Problem:
    return Problem(
        category=ProblemCategory.SINGLE_GATE_OUTPUT,
        difficulty="beginner",
        question_text="q",
        answer_format=fmt,
        correct_answer=correct,
        choices=choices,
        circuit_png=None,
        aux_circuit_png=None,
        matrix_str=None,
        state_str=None,
        solution_steps=["s"],
        key_concepts=["k"],
    )


def _sv(amps) -> str:
    return "[" + ", ".join(repr(complex(a)) for a in amps) + "]"


# ── Multiple choice ───────────────────────────────────────────────────────────

def test_mc_correct_and_wrong_and_invalid():
    p = _problem(AnswerFormat.MULTIPLE_CHOICE, "2", ["a", "b", "c", "d"])
    ok = grade(p, "2")
    assert isinstance(ok, Attempt) and ok.is_correct and ok.score == 10
    assert "c" in ok.feedback

    bad = grade(p, "0")
    assert not bad.is_correct and bad.score == 0
    assert "a" in bad.feedback and "c" in bad.feedback

    junk = grade(p, "banana")
    assert not junk.is_correct and junk.score == 0


# ── Numeric ───────────────────────────────────────────────────────────────────

def test_numeric_exact_partial_and_wrong():
    p = _problem(AnswerFormat.NUMERIC, 0.5)
    assert grade(p, "0.5").score == 10
    assert grade(p, f"{0.5 + NUMERIC_TOLERANCE / 2}").is_correct
    close = grade(p, "0.53")            # within 0.05 -> half credit
    assert not close.is_correct and close.score == 5
    far = grade(p, "0.9")
    assert not far.is_correct and far.score == 0
    junk = grade(p, "one half")               # unparseable -> wrong, not an exception
    assert not junk.is_correct and junk.score == 0 and "0.5" in junk.feedback




# ── State vector ──────────────────────────────────────────────────────────────

PLUS = [1 / math.sqrt(2), 1 / math.sqrt(2)]


GLOBAL_PHASES = [1, -1, 1j, -1j, cmath.exp(1j * math.pi / 4), cmath.exp(-1j * 2.3)]


def test_statevector_grading_is_global_phase_invariant():
    bell = [1 / math.sqrt(2), 0, 0, 1 / math.sqrt(2)]
    for target in (PLUS, bell):
        p = _problem(AnswerFormat.STATE_VECTOR, _sv(target))
        for phase in GLOBAL_PHASES:
            a = grade(p, _sv([phase * x for x in target]))
            assert a.is_correct and a.score == 10, (phase, a.feedback)


def test_statevector_accepts_unnormalised_input_but_rejects_relative_phase():
    p = _problem(AnswerFormat.STATE_VECTOR, _sv(PLUS))
    assert grade(p, "[1, 1]").is_correct                       # normalised internally
    assert grade(p, "[3, 3]").is_correct
    minus = grade(p, "[1, -1]")                               # |-> is orthogonal to |+>
    assert not minus.is_correct and minus.score == 0
    # Bell state vs product state: overlap 1/sqrt(2) -> partial credit band
    bell = _problem(AnswerFormat.STATE_VECTOR, _sv([1 / math.sqrt(2), 0, 0, 1 / math.sqrt(2)]))
    near = grade(bell, "[1, 0, 0, 0]")
    assert not near.is_correct and near.score in (0, 5)


def test_statevector_rejects_zero_vector_and_garbage():
    p = _problem(AnswerFormat.STATE_VECTOR, _sv(PLUS))
    zero = grade(p, "[0, 0]")
    assert not zero.is_correct and zero.score == 0
    junk = grade(p, "|+>")
    assert not junk.is_correct and junk.score == 0
    assert "parse" in junk.feedback.lower()


# ── Robustness ────────────────────────────────────────────────────────────────

def test_free_form_falls_through_without_crediting():
    p = _problem(AnswerFormat.FREE_FORM, "")
    a = grade(p, "some essay")
    assert not a.is_correct and a.score == 0


def test_grade_never_raises_on_corrupt_problem():
    broken = _problem(AnswerFormat.MULTIPLE_CHOICE, "not-an-int", ["a", "b"])
    a = grade(broken, "0")
    assert isinstance(a, Attempt) and not a.is_correct and a.score == 0
    assert "error" in a.feedback.lower()
