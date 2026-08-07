"""Card: sm_shadow_tomography"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='sm_shadow_tomography',
    category='States & Measurement',
    front='Shadow tomography: main result',
    back='Predict M linear functions Tr(Oᵢρ) to ε precision using only O(log²(M) ε⁻⁴ log d) copies of ρ — exponentially fewer than full tomography (Aaronson 2018).',
)
