"""
Auto-grader for MULTIPLE_CHOICE, NUMERIC, and STATE_VECTOR answer formats.
All grading is done locally via Qiskit — no Claude call needed.
"""

from __future__ import annotations
from core.models import Problem, Attempt, AnswerFormat
from config import NUMERIC_TOLERANCE


def grade(problem: Problem, user_answer: str) -> Attempt:
    """Grade a user answer and return an Attempt. Never raises."""
    try:
        if problem.answer_format == AnswerFormat.MULTIPLE_CHOICE:
            return _grade_mc(problem, user_answer)
        elif problem.answer_format == AnswerFormat.NUMERIC:
            return _grade_numeric(problem, user_answer)
        elif problem.answer_format == AnswerFormat.STATE_VECTOR:
            return _grade_statevector(problem, user_answer)
        else:
            # FREE_FORM — shouldn't reach auto_grader
            return Attempt(problem, user_answer, False, 0, "Requires manual grading.")
    except Exception as exc:
        return Attempt(problem, user_answer, False, 0, f"Grading error: {exc}")


# ── Multiple choice ───────────────────────────────────────────────────────────

def _grade_mc(problem: Problem, user_answer: str) -> Attempt:
    correct_idx = int(problem.correct_answer)
    try:
        user_idx = int(user_answer)
    except ValueError:
        return Attempt(problem, user_answer, False, 0, "Invalid selection.")

    is_correct = user_idx == correct_idx
    score = 10 if is_correct else 0

    if is_correct:
        feedback = "Correct!"
        if problem.choices:
            feedback += f" The answer is: {problem.choices[correct_idx]}"
    else:
        correct_label = problem.choices[correct_idx] if problem.choices else str(correct_idx)
        user_label = problem.choices[user_idx] if (problem.choices and 0 <= user_idx < len(problem.choices)) else str(user_idx)
        feedback = f"Incorrect. You chose: {user_label}\nCorrect answer: {correct_label}"

    return Attempt(problem, user_answer, is_correct, score, feedback)


# ── Numeric ───────────────────────────────────────────────────────────────────

def _grade_numeric(problem: Problem, user_answer: str) -> Attempt:
    try:
        user_val = float(user_answer.strip())
        correct_val = float(problem.correct_answer)
    except ValueError:
        return Attempt(problem, user_answer, False, 0,
                       f"Could not parse your answer as a number. Correct: {problem.correct_answer}")

    diff = abs(user_val - correct_val)
    is_correct = diff <= NUMERIC_TOLERANCE
    if is_correct:
        score = 10
        feedback = f"Correct! {correct_val:.6g}"
    elif diff <= 0.05:
        score = 5
        feedback = f"Close but not within tolerance. Your answer: {user_val:.6g}, Correct: {correct_val:.6g}"
    else:
        score = 0
        feedback = f"Incorrect. Your answer: {user_val:.6g}, Correct: {correct_val:.6g}"

    return Attempt(problem, user_answer, is_correct, score, feedback)


# ── State vector ──────────────────────────────────────────────────────────────

def _grade_statevector(problem: Problem, user_answer: str) -> Attempt:
    """Compare user-entered amplitudes to the correct state vector."""
    import ast, numpy as np
    try:
        parsed = ast.literal_eval(user_answer)
        user_vec = np.array(parsed, dtype=complex)
        correct_vec = np.array(ast.literal_eval(str(problem.correct_answer)), dtype=complex)
    except Exception:
        return Attempt(problem, user_answer, False, 0,
                       "Could not parse state vector. Format: [a+bj, c+dj, ...]")

    # Normalise both
    user_norm = np.linalg.norm(user_vec)
    correct_norm = np.linalg.norm(correct_vec)
    if user_norm < 1e-12 or correct_norm < 1e-12:
        return Attempt(problem, user_answer, False, 0, "Zero-length vector submitted.")
    user_vec = user_vec / user_norm
    correct_vec = correct_vec / correct_norm

    # Check equality up to global phase
    inner = abs(np.dot(user_vec.conj(), correct_vec))
    is_correct = abs(inner - 1.0) < NUMERIC_TOLERANCE
    score = 10 if is_correct else (5 if inner > 0.9 else 0)
    feedback = ("Correct (up to global phase)!" if is_correct
                else f"Incorrect. Overlap = {inner:.4f}. Correct: {problem.correct_answer}")

    return Attempt(problem, user_answer, is_correct, score, feedback)
