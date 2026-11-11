"""Shared dataclasses — the only types that cross module boundaries."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class QuizConfig:
    subjects: list[str]
    difficulty: Optional[str]          # None → randomise each question
    question_types: list[str]
    question_count: int


@dataclass
class Question:
    subject: str
    topic: str
    difficulty: str
    question_type: str
    text: str
    hints: list[str] = field(default_factory=list)


@dataclass
class Evaluation:
    score: int                         # 0–10
    verdict: str                       # "Correct" | "Partially correct" | "Incorrect"
    feedback: str
    model_answer: str
    key_points_missed: list[str] = field(default_factory=list)
    follow_up: str = ""


@dataclass
class QuestionRecord:
    question: Question
    user_answer: str
    evaluation: Evaluation
    question_id: str = ""          # stable key used by SRS (subject::topic)
    elapsed_seconds: int = 0       # seconds spent on this question


@dataclass
class SessionStats:
    total_generated: int = 0
    answered: int = 0
    skipped: int = 0
    history: list[QuestionRecord] = field(default_factory=list)

    @property
    def average_score(self) -> float:
        scores = [r.evaluation.score for r in self.history]
        return sum(scores) / len(scores) if scores else 0.0

    def scores_by_subject(self) -> dict[str, list[int]]:
        result: dict[str, list[int]] = {}
        for record in self.history:
            result.setdefault(record.question.subject, []).append(record.evaluation.score)
        return result
