"""Card: sm_SIC_POVM"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='sm_SIC_POVM',
    category='States & Measurement',
    front='SIC-POVM for 1 qubit: how many elements?',
    back='4 rank-1 elements {Mᵢ = |ψᵢ⟩⟨ψᵢ|/2} where inner products |⟨ψᵢ|ψⱼ⟩|² = 1/3 for i≠j — symmetric informationally complete POVM',
)
