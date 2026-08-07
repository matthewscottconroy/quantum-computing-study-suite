"""Card: qi_von_neumann"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qi_von_neumann',
    category='Quantum Info',
    front='Von Neumann entropy formula',
    back='S(ρ) = -Tr(ρ log₂ ρ) = -Σ λᵢ log₂ λᵢ   where λᵢ are eigenvalues of ρ',
)
