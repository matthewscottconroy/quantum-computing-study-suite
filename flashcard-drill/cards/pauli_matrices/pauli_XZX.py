"""Card: pauli_XZX"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='pauli_XZX',
    category='Pauli Matrices',
    front='XZX = ?',
    back='XZX = −Z.  X and Z anticommute, so XZX = X(−XZ) = −Z.',
)
