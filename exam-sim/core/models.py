"""Domain models for exam-sim."""
from __future__ import annotations
from dataclasses import dataclass, field

import common_path  # noqa: F401  (puts the repo root on sys.path)

from common.choices import resolve_order


@dataclass
class Question:
    id: str
    section: str
    question: str               # may contain a fenced ``` code block
    options: list[str]          # exactly 4
    correct_index: int
    explanation: str
    difficulty: str             # "easy" | "medium" | "hard"


@dataclass
class ExamAttempt:
    """One question inside a running session."""
    question: Question
    chosen_index: int | None = None
    flagged: bool = False
    # 1-4 self-rated confidence, captured before the answer is revealed
    # (None = not rated / prompt switched off). In-session only; the graded
    # pairing is written to confidence.json when the session is submitted.
    confidence: int | None = None
    # Display order of the options for this attempt: option_order[row] is the
    # *bank* index shown in that row (see common.choices). In-session only.
    # chosen_index above is always a bank index, never a row, so grading and
    # everything written to disk are independent of the order. Empty = bank
    # order, which is what an attempt built without one falls back to.
    option_order: list[int] = field(default_factory=list)

    @property
    def answered(self) -> bool:
        return self.chosen_index is not None

    def display_order(self) -> list[int]:
        """option_order if it is a valid permutation, else bank order."""
        return resolve_order(self.option_order, len(self.question.options))

    @property
    def correct(self) -> bool:
        return self.chosen_index == self.question.correct_index


@dataclass
class ExamResult:
    """A finished full-exam or sprint session."""
    mode: str                   # "full" | "sprint"
    attempts: list[ExamAttempt] = field(default_factory=list)
    duration_secs: float = 0.0

    @property
    def total(self) -> int:
        return len(self.attempts)

    @property
    def correct(self) -> int:
        return sum(1 for a in self.attempts if a.correct)

    @property
    def missed(self) -> list[ExamAttempt]:
        return [a for a in self.attempts if not a.correct]

    def section_breakdown(self) -> dict[str, dict[str, int]]:
        out: dict[str, dict[str, int]] = {}
        for a in self.attempts:
            bucket = out.setdefault(a.question.section, {"total": 0, "correct": 0})
            bucket["total"] += 1
            if a.correct:
                bucket["correct"] += 1
        return out
