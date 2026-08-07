"""Card: ec_perfect_5"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='ec_perfect_5',
    category='Error Correction',
    front='[[5,1,3]] code: why is it special?',
    back='Fewest possible physical qubits to encode 1 logical qubit and correct any single-qubit error.  Stabilizers: XZZXI, IXZZX, XIXZZ, ZXIXZ.',
)
