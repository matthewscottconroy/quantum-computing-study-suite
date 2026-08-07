"""Card: qi_schmidt"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qi_schmidt',
    category='Quantum Info',
    front='Schmidt decomposition of |ψ⟩_AB',
    back='|ψ⟩ = Σᵢ λᵢ|αᵢ⟩⊗|βᵢ⟩  where λᵢ>0 are Schmidt coefficients, Σλᵢ²=1.  Schmidt rank = # nonzero λᵢ.',
)
