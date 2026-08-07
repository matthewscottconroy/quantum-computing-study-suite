"""Card: ec_params"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='ec_params',
    category='Error Correction',
    front='[[n, k, d]] code: what do n, k, d mean?',
    back='n = physical qubits, k = logical qubits encoded, d = code distance (minimum weight of a logical operator)',
)
