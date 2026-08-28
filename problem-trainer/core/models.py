"""Domain models for problem-trainer."""
from __future__ import annotations
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Mode 1 — long-form problem sets
# ---------------------------------------------------------------------------

@dataclass
class Part:
    part_id: str
    prompt: str
    points: int
    rubric: list[str]          # grader-facing: what earns credit
    model_solution: str


@dataclass
class Problem:
    id: str
    topic: str
    title: str
    statement: str
    parts: list[Part]

    @property
    def total_points(self) -> int:
        return sum(p.points for p in self.parts)


@dataclass
class GradeResult:
    score: int                 # 0–10 for the part
    feedback: str
    missed_points: list[str] = field(default_factory=list)


@dataclass
class PartState:
    """Mutable per-session state of one problem part."""
    part: Part
    answer: str = ""
    result: GradeResult | None = None
    tries: int = 0
    solution_revealed: bool = False

    @property
    def score(self) -> int:
        return self.result.score if self.result else 0


# ---------------------------------------------------------------------------
# Mode 2 — guided Socratic derivations
# ---------------------------------------------------------------------------

@dataclass
class Step:
    step_id: str
    prompt: str                # Socratic question posed to the user
    expected: str              # grader-facing description of a correct step
    hint: str
    model_step: str


@dataclass
class Derivation:
    id: str
    title: str
    goal: str
    steps: list[Step]


@dataclass
class StepCheck:
    verdict: str               # "accept" | "needs_work"
    nudge: str = ""

    @property
    def accepted(self) -> bool:
        return self.verdict == "accept"


@dataclass
class StepState:
    step: Step
    answer: str = ""
    tries: int = 0
    accepted: bool = False
    model_revealed: bool = False


# ---------------------------------------------------------------------------
# Sessions
# ---------------------------------------------------------------------------

@dataclass
class AttemptRecord:
    """One finished problem or derivation. score is on a 0–10 scale."""
    problem_id: str
    kind: str                  # "problem" | "derivation"
    score: float
    title: str = ""


@dataclass
class SessionStats:
    attempts: list[AttemptRecord] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.attempts)

    @property
    def avg_score(self) -> float:
        if not self.attempts:
            return 0.0
        return sum(a.score for a in self.attempts) / len(self.attempts)


def problem_score(states: list[PartState]) -> float:
    """Points-weighted problem score on a 0–10 scale (ungraded parts count 0)."""
    total_pts = sum(s.part.points for s in states)
    if total_pts == 0:
        return 0.0
    earned = sum(s.part.points * (s.score / 10.0) for s in states)
    return round(10.0 * earned / total_pts, 2)


def derivation_score(states: list[StepState]) -> float:
    """Fraction of steps accepted without a model reveal, scaled 0–10."""
    if not states:
        return 0.0
    clean = sum(1 for s in states if s.accepted and not s.model_revealed)
    return round(10.0 * clean / len(states), 2)
