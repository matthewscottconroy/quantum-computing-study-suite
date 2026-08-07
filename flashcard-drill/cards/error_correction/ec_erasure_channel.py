"""Card: ec_erasure_channel"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='ec_erasure_channel',
    category='Error Correction',
    front='Erasure channel and QEC capacity',
    back='Each qubit erased (location known) with probability ε.  Capacity = 1−2ε — better than depolarisation because known-location erasure is correctable with fewer overhead qubits.',
)
