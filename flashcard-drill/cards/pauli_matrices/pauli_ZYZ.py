"""Card: pauli_ZYZ"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='pauli_ZYZ',
    category='Pauli Matrices',
    front='ZYZ = ?',
    back='ZYZ = −Y.  Z and Y anticommute, so ZYZ = −Y.',
)
