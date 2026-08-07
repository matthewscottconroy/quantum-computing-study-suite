"""Card: qi_dense_coding"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qi_dense_coding',
    category='Quantum Info',
    front='Quantum dense coding steps',
    back='1) Alice applies I/X/Z/XZ to her half of shared Bell pair encoding 2 bits.  2) Sends qubit to Bob.  3) Bob does Bell measurement to recover 2 bits.',
)
