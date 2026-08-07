"""Domain models for paper-drill."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum


class Verdict(str, Enum):
    CORRECT   = "Correct"
    PARTIAL   = "Partially correct"
    INCORRECT = "Incorrect"


@dataclass
class Question:
    index: int
    text: str
    q_type: str      # "factual" | "conceptual" | "derivation"


@dataclass
class DrillConfig:
    paper_text: str
    paper_title: str
    question_count: int = 5


@dataclass
class Evaluation:
    score: int          # 0–10
    verdict: Verdict
    feedback: str
    model_answer: str = ""


@dataclass
class QuestionAttempt:
    question: Question
    answer_text: str
    evaluation: Evaluation | None = None


@dataclass
class SessionStats:
    title: str = ""
    total: int = 0
    scores: list[int] = field(default_factory=list)

    @property
    def average(self) -> float:
        return sum(self.scores) / len(self.scores) if self.scores else 0.0
