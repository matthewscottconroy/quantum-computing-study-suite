"""Card: thm_bauer_max"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='thm_bauer_max',
    category='Theorems',
    front='Bauer maximum principle for quantum optimization',
    back='The maximum of a linear functional over a compact convex set (e.g., density matrices) is always achieved at an extreme point (a pure state).  Justifies searching pure states for optimal inputs.',
)
