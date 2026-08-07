"""Card: cx_oracle_sep"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='cx_oracle_sep',
    category='Complexity',
    front='Does BQP ≠ P have a known oracle separation?',
    back="Yes — Bernstein-Vazirani and Simon's algorithm provide oracle separations",
)
