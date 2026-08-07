"""Card: cx_oracle_limits"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='cx_oracle_limits',
    category='Complexity',
    front='Limitation of oracle separations',
    back='Oracle separations (e.g., BQP ≠ BPP relative to a random oracle) do not imply separations in the unrelativized world.  They motivate but do not prove absolute complexity separations.',
)
