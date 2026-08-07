"""Card: qi_holevo_capacity"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qi_holevo_capacity',
    category='Quantum Info',
    front='Holevo capacity χ of a quantum channel',
    back='χ = S(Σpᵢρᵢ) - Σpᵢ S(ρᵢ)   — upper bound on classical info transmittable per channel use',
)
