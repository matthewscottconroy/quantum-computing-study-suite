"""Card: pauli_raising_op"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='pauli_raising_op',
    category='Pauli Matrices',
    front='Raising operator σ₊ in terms of X and Y',
    back='σ₊ = (X + iY)/2 = |0⟩⟨1| — maps |1⟩ to |0⟩ and annihilates |0⟩.  Used in spin and qubit Hamiltonians.',
)
