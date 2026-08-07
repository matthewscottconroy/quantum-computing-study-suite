"""Card: alg_QAOA_layers"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='alg_QAOA_layers',
    category='Algorithms',
    front='QAOA: what are the two operators per layer?',
    back='Problem unitary U_C = e^{-iγC} and mixing unitary U_B = e^{-iβB}  (alternated p times)',
)
