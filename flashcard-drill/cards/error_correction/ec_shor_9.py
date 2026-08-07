"""Card: ec_shor_9"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='ec_shor_9',
    category='Error Correction',
    front='Shor [[9,1,3]] code: structure?',
    back='Concatenation of 3-qubit phase-flip code (outer) and 3-qubit bit-flip code (inner).  First code to protect against arbitrary single-qubit errors.',
)
