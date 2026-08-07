"""Card: ec_stabilizer_group"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='ec_stabilizer_group',
    category='Error Correction',
    front='Stabilizer group of an [[n,k,d]] code',
    back='Abelian subgroup S of n-qubit Pauli group (no −I) with |S|=2^{n−k}.  Code space = simultaneous +1 eigenspace of all elements of S.',
)
