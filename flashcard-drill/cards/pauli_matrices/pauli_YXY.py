"""Card: pauli_YXY"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='pauli_YXY',
    category='Pauli Matrices',
    front='YXY = ?',
    back='YXY = −X.  Conjugating X by Y flips the sign; Y-rotation by π inverts the x-axis.',
)
