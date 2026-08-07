"""Card: sm_plus_vec"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='sm_plus_vec',
    category='States & Measurement',
    front='Column vector for |+⟩',
    back='|+⟩ = [1/√2, 1/√2]ᵀ = (|0⟩+|1⟩)/√2   — X eigenstate with eigenvalue +1',
)
