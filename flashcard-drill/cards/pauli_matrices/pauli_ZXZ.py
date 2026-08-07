"""Card: pauli_ZXZ"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='pauli_ZXZ',
    category='Pauli Matrices',
    front='ZXZ = ?',
    back='ZXZ = −X.  Z and X anticommute: ZXZ = Z(−ZX) = −X.',
)
