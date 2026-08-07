"""Card: sm_POVM_def"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='sm_POVM_def',
    category='States & Measurement',
    front='POVM definition',
    back='Positive Operator-Valued Measure: set {Mᵢ} with Mᵢ ≥ 0 and Σᵢ Mᵢ = I.  P(i) = Tr(Mᵢρ).  More general than projective measurement.',
)
