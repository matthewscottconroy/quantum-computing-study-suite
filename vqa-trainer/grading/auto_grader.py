"""Auto-graders for MC and numeric VQA problems."""
from __future__ import annotations
from core.models import Problem, Attempt, Verdict, GradeMode


def grade_mc(problem: Problem, answer: str) -> Attempt:
    letter_map = {"A": 0, "B": 1, "C": 2, "D": 3}
    idx = letter_map.get(answer.strip().upper(), -1)
    correct = idx == problem.correct_index
    score   = 10 if correct else 0
    verdict = Verdict.CORRECT if correct else Verdict.INCORRECT
    feedback = (
        f"Correct! {problem.explanation}" if correct else
        f"Incorrect. The right answer was {chr(65 + problem.correct_index)}: "
        f"{problem.choices[problem.correct_index]}\n\n{problem.explanation}"
    )
    return Attempt(
        problem=problem, answer=answer, score=score, verdict=verdict,
        feedback=feedback,
        model_answer=problem.choices[problem.correct_index] if problem.choices else "",
    )


def grade_numeric(problem: Problem, answer: str) -> Attempt:
    try:
        value = float(answer.strip().replace(",", "."))
    except ValueError:
        return Attempt(
            problem=problem, answer=answer,
            score=0, verdict=Verdict.INCORRECT,
            feedback="Could not parse your answer as a number.",
            model_answer=str(problem.correct_value),
        )

    diff = abs(value - problem.correct_value)
    if diff <= problem.tolerance:
        score, verdict = 10, Verdict.CORRECT
        feedback = f"Correct! {problem.explanation}"
    elif diff <= problem.tolerance * 20:
        # Close but not exact — partial credit scaled by proximity
        score = max(4, round(10 * (1 - diff / (problem.tolerance * 20))))
        verdict = Verdict.PARTIAL
        feedback = (
            f"Close — got {value:.4g}, expected {problem.correct_value:.4g}. "
            f"Check your arithmetic.\n\n{problem.explanation}"
        )
    else:
        score, verdict = 0, Verdict.INCORRECT
        feedback = (
            f"Incorrect. Got {value}, expected {problem.correct_value:.4g}.\n\n{problem.explanation}"
        )
    return Attempt(
        problem=problem, answer=answer, score=score, verdict=verdict,
        feedback=feedback, model_answer=f"{problem.correct_value:.4g}",
    )
