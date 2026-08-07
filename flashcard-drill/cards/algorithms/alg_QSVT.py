"""Card: alg_QSVT"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='alg_QSVT',
    category='Algorithms',
    front='Quantum singular value transformation (QSVT)',
    back='Unifying framework applying polynomial transformations to singular values of a block-encoded matrix.  Subsumes QFT, QPE, Grover, HHL, and quantum simulation as special cases.',
)
