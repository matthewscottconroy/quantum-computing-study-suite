"""Card: pauli_lowering_op"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='pauli_lowering_op',
    category='Pauli Matrices',
    front='Lowering operator σ₋ in terms of X and Y',
    back='σ₋ = (X − iY)/2 = |1⟩⟨0| — maps |0⟩ to |1⟩ and annihilates |1⟩.  Conjugate of σ₊.',
)
