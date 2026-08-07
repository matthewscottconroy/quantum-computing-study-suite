"""Card: qi_PPT"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qi_PPT',
    category='Quantum Info',
    front='PPT (Peres-Horodecki) criterion',
    back='If ρ is separable then (I⊗T)ρ ≥ 0 (partial transpose is PSD).  Violation ⟹ entangled.  Sufficient for 2×2 and 2×3.',
)
