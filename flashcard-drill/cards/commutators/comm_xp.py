"""Card: comm_xp"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='comm_xp',
    category='Commutators',
    front='[x̂, p̂] = ?',
    back='[x̂, p̂] = iℏ — the canonical position-momentum commutation relation; implies Δx·Δp ≥ ℏ/2.',
)
