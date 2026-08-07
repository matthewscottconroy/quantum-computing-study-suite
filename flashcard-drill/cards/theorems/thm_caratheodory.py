"""Card: thm_caratheodory"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='thm_caratheodory',
    category='Theorems',
    front='Carathéodory theorem for quantum states',
    back='Any mixed state ρ on a d-dimensional Hilbert space can be written as a convex combination of at most d² pure states — a finite decomposition always suffices.',
)
