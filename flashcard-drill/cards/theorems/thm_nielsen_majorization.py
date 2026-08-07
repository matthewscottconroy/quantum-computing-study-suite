"""Card: thm_nielsen_majorization"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='thm_nielsen_majorization',
    category='Theorems',
    front="Nielsen's theorem on pure-state entanglement conversion",
    back='|ψ⟩ → LOCC |φ⟩ is possible iff the Schmidt coefficients of |ψ⟩ are majorized by those of |φ⟩: λ↓(ψ) ≺ λ↓(φ).',
)
