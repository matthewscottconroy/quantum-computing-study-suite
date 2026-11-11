"""Auto-grader for multiple-choice QEC problems."""
from quantum_study.qec_trainer.core.models import Problem, Attempt, Verdict


def grade_mc(problem: Problem, answer: str) -> Attempt:
    """Grade a multiple-choice answer.

    ``answer`` is the *bank* letter: 'A' means ``problem.choices[0]``, whatever
    row the problem screen showed it in. The feedback therefore names the
    right choice by its text, never by a letter the learner did not see.
    """
    letter_map = {"A": 0, "B": 1, "C": 2, "D": 3}
    idx = letter_map.get(answer.strip().upper(), -1)
    correct = idx == problem.correct_index

    score = 10 if correct else 0
    verdict = Verdict.CORRECT if correct else Verdict.INCORRECT
    feedback = (
        f"Correct! {problem.explanation}" if correct
        else f"Incorrect. The right answer was: "
             f"{problem.choices[problem.correct_index]}\n\n{problem.explanation}"
    )
    return Attempt(
        problem=problem,
        answer=answer,
        score=score,
        verdict=verdict,
        feedback=feedback,
        model_answer=problem.choices[problem.correct_index] if problem.choices else "",
    )
