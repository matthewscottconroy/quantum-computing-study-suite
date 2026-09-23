"""Domain models for vqa-trainer."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum


class GradeMode(str, Enum):
    AUTO   = "auto"      # exact numeric check (parameter shift, etc.)
    MC     = "mc"        # multiple-choice
    CLAUDE = "claude"    # open-ended, Claude grades


class Verdict(str, Enum):
    CORRECT   = "Correct"
    PARTIAL   = "Partially correct"
    INCORRECT = "Incorrect"


@dataclass
class Problem:
    id: str
    category: str
    difficulty: str
    question: str
    choices: list[str] = field(default_factory=list)
    correct_index: int = -1
    correct_value: float | None = None     # for numeric auto-grade
    tolerance: float = 1e-6               # absolute tolerance for numeric check
    explanation: str = ""
    hints: list[str] = field(default_factory=list)
    grade_mode: GradeMode = GradeMode.MC


@dataclass
class TrainerConfig:
    categories: list[str]
    difficulty: str | None
    problem_count: int
    flagged_only: bool = False


@dataclass
class Attempt:
    problem: Problem
    answer: str
    score: int = 0
    verdict: Verdict = Verdict.INCORRECT
    feedback: str = ""
    model_answer: str = ""
    hints_used: int = 0
    elapsed_secs: int = 0


@dataclass
class SessionStats:
    total: int = 0
    correct: int = 0
    attempts: list[Attempt] = field(default_factory=list)

    @property
    def accuracy(self) -> float:
        return self.correct / self.total if self.total else 0.0


def answer_texts(attempt: Attempt) -> tuple[str, str]:
    """(your answer, correct answer) as short display strings.

    Pure and Qt-free, so the mistake journal records what the learner actually
    chose ("B. Hardware-efficient ansatz") rather than a bare letter.
    """
    problem = attempt.problem
    given = (attempt.answer or "").strip()
    correct = (attempt.model_answer or "").strip()

    if problem.grade_mode is GradeMode.MC and problem.choices:
        idx = {"A": 0, "B": 1, "C": 2, "D": 3}.get(given.upper(), -1)
        if 0 <= idx < len(problem.choices):
            given = f"{chr(65 + idx)}. {problem.choices[idx]}"
        elif not given:
            given = "(no answer)"
        ci = problem.correct_index
        if 0 <= ci < len(problem.choices):
            correct = f"{chr(65 + ci)}. {problem.choices[ci]}"
    elif problem.grade_mode is GradeMode.AUTO and not correct:
        correct = "" if problem.correct_value is None else f"{problem.correct_value:.4g}"

    if not correct:
        correct = problem.explanation or ""
    return given or "(no answer)", correct
