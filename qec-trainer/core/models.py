"""Domain models for qec-trainer."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum


class GradeMode(str, Enum):
    AUTO   = "auto"      # exact match or structured check
    CLAUDE = "claude"    # open-ended, Claude grades


class Verdict(str, Enum):
    CORRECT   = "Correct"
    PARTIAL   = "Partially correct"
    INCORRECT = "Incorrect"


@dataclass
class Problem:
    id: str
    category: str
    difficulty: str           # "beginner" | "intermediate" | "advanced"
    question: str
    choices: list[str]        # empty for free-form
    correct_index: int = -1   # -1 for free-form
    explanation: str = ""
    hints: list[str] = field(default_factory=list)
    grade_mode: GradeMode = GradeMode.AUTO


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
