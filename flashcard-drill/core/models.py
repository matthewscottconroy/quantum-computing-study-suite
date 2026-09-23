"""Domain models for flashcard-drill."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum

from core.scheduler import ReviewOutcome


class Rating(str, Enum):
    GOT_IT  = "got_it"
    UNSURE  = "unsure"
    MISSED  = "missed"


@dataclass
class Flashcard:
    id: str
    category: str
    front: str
    back: str
    latex: bool = False         # render back with math markers


@dataclass
class DrillConfig:
    categories: list[str]
    card_count: int = 20
    timer_secs: int = 0         # 0 = unlimited
    flagged_only: bool = False
    due_only: bool = False      # SM-2 "Due today" pull instead of weighted sampling


@dataclass
class CardResult:
    card_id: str
    category: str
    rating: Rating
    elapsed_secs: float | None = None   # show -> rate wall time; None when unknown


@dataclass
class SessionStats:
    total: int = 0
    got_it: int = 0
    unsure: int = 0
    missed: int = 0
    results: list[CardResult] = field(default_factory=list)
    # One ReviewOutcome per rated card (SM-2 before/after).  Summary-screen only:
    # never written to flashcard_history.json.
    schedule: list[ReviewOutcome] = field(default_factory=list)

    @property
    def graduated(self) -> int:
        return sum(1 for o in self.schedule if o.graduated)

    @property
    def lapsed(self) -> int:
        return sum(1 for o in self.schedule if o.lapsed)

    @property
    def pct_known(self) -> float:
        return self.got_it / self.total if self.total else 0.0
