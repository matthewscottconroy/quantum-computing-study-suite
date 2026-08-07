"""Card: alg_block_encoding"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='alg_block_encoding',
    category='Algorithms',
    front='Block encoding of a non-unitary matrix A',
    back='U is a block encoding of A/α if A/α appears as the top-left block of U.  Enables QSVT to process non-unitary operators on a quantum computer.',
)
