"""Shared dataclasses for circuit-trainer."""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any


class AnswerFormat(Enum):
    MULTIPLE_CHOICE  = auto()   # 4 options, auto-graded
    NUMERIC          = auto()   # single float, auto-graded with tolerance
    STATE_VECTOR     = auto()   # list of complex amplitudes, auto-graded
    FREE_FORM        = auto()   # written text, Claude-graded


class ProblemCategory(Enum):
    SINGLE_GATE_OUTPUT    = "Single-gate output"
    GATE_SEQUENCE         = "Gate sequence"
    MEASUREMENT_PROBS     = "Measurement probabilities"
    GATE_IDENTITY         = "Gate / matrix identification"
    CIRCUIT_UNITARY       = "Circuit unitary"
    ENTANGLEMENT          = "Entanglement detection"
    MULTI_QUBIT_OUTPUT    = "Multi-qubit circuit output"
    CIRCUIT_EQUIVALENCE   = "Circuit equivalence"
    NOTATION_READING      = "Notation reading"
    CIRCUIT_COMPOSITION   = "Circuit composition"
    NOISE_CHANNEL         = "Noise channel"
    CIRCUIT_EXPLANATION   = "Circuit explanation"


@dataclass
class Problem:
    category: ProblemCategory
    difficulty: str                     # "beginner" | "intermediate" | "advanced"
    question_text: str
    answer_format: AnswerFormat
    correct_answer: Any                 # type varies by format
    choices: list[str] | None           # only for MULTIPLE_CHOICE
    circuit_png: bytes | None           # rendered main circuit
    aux_circuit_png: bytes | None       # second circuit (for equivalence problems)
    matrix_str: str | None              # formatted matrix (for identification problems)
    state_str: str | None               # formatted state vector
    solution_steps: list[str]           # step-by-step worked solution
    key_concepts: list[str]             # concepts tested
    hints: list[str] = field(default_factory=list)
    problem_id: str | None = None       # stable ID for SRS tracking


@dataclass
class Attempt:
    problem: Problem
    user_answer: str
    is_correct: bool
    score: int                          # 0–10
    feedback: str
    model_answer: str = ""
    follow_up: str = ""
    elapsed_secs: int = 0               # seconds spent on this problem


@dataclass
class TrainerConfig:
    categories: list[ProblemCategory]
    difficulty: str | None              # None → mixed
    problem_count: int
    sprint: bool = False                # timed sprint mode (60s per question)


@dataclass
class SessionStats:
    total: int = 0
    correct: int = 0
    partial: int = 0
    wrong: int = 0
    attempts: list[Attempt] = field(default_factory=list)

    @property
    def accuracy(self) -> float:
        return self.correct / self.total if self.total else 0.0

    def scores_by_category(self) -> dict[str, list[int]]:
        result: dict[str, list[int]] = {}
        for a in self.attempts:
            cat = a.problem.category.value
            result.setdefault(cat, []).append(a.score)
        return result
