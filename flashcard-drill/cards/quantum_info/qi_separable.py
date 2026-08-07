"""Card: qi_separable"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qi_separable',
    category='Quantum Info',
    front='Definition of a separable state',
    back='ρ_AB = Σᵢ pᵢ ρᵢ_A ⊗ ρᵢ_B   (convex combination of product states).  Non-separable = entangled.',
)
