"""Domain models for flashcard-drill."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum


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

    @property
    def pct_known(self) -> float:
        return self.got_it / self.total if self.total else 0.0
