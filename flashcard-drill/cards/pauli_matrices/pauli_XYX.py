"""Card: pauli_XYX"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='pauli_XYX',
    category='Pauli Matrices',
    front='XYX = ?',
    back='XYX = −Y.  Conjugating Y by X flips its sign; in Bloch picture, X-rotation by π inverts the y-axis.',
)
