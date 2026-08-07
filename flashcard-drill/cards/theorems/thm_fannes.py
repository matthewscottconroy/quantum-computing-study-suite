"""Card: thm_fannes"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='thm_fannes',
    category='Theorems',
    front='Fannes inequality',
    back='|S(ρ) − S(σ)| ≤ T log(d−1) + H(T,1−T)  where T = ½‖ρ−σ‖₁ — entropy is continuous in trace distance',
)
