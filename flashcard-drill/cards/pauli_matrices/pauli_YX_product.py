"""Card: pauli_YX_product"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='pauli_YX_product',
    category='Pauli Matrices',
    front='YX = ?',
    back='YX = −iZ   (note: XY=+iZ so YX=−iZ, consistent with anticommutation {X,Y}=0)',
)
