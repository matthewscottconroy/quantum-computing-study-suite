"""Card: ec_cat_qubit"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='ec_cat_qubit',
    category='Error Correction',
    front='Cat qubit: what is special about its error rates?',
    back='Exponentially biased noise: Z (dephasing) errors grow polynomially with cat size, while X (bit-flip) errors are exponentially suppressed.  Enables tailored QEC.',
)
