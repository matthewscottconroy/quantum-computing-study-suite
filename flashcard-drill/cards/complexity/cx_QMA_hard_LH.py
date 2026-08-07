"""Card: cx_QMA_hard_LH"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='cx_QMA_hard_LH',
    category='Complexity',
    front='What is the canonical QMA-complete problem?',
    back='Local Hamiltonian (LH-MIN): given a k-local Hamiltonian, decide if ground energy ≤ a or ≥ b (with b−a ≥ 1/poly).  QMA-complete for k ≥ 2 (Kitaev).',
)
