"""Domain models for exam-sim."""
from __future__ import annotations
from dataclasses import dataclass, field


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

    @property
    def answered(self) -> bool:
        return self.chosen_index is not None

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
