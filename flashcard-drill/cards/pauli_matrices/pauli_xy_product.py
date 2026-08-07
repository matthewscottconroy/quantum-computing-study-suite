"""Card: pauli_xy_product"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='pauli_xy_product',
    category='Pauli Matrices',
    front='XY = ?',
    back='XY = iZ   (cyclic: XY=iZ, YZ=iX, ZX=iY)',
)
