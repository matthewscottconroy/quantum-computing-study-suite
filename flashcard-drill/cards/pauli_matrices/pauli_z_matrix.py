"""Card: pauli_z_matrix"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='pauli_z_matrix',
    category='Pauli Matrices',
    front='Matrix form of Z (phase-flip)',
    back='Z = [[1,0],[0,-1]]   — maps |0⟩→|0⟩, |1⟩→-|1⟩',
)
