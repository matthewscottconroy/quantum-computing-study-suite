"""Card: thm_surface_threshold"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='thm_surface_threshold',
    category='Theorems',
    front='Approximate threshold for surface code',
    back='~1% physical error rate.  Below this, logical error rate decreases exponentially with code distance.',
)
