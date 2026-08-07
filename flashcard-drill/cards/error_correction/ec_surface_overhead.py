"""Card: ec_surface_overhead"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='ec_surface_overhead',
    category='Error Correction',
    front='Surface code qubit overhead?',
    back='~2d² physical qubits per logical qubit for distance-d surface code (d data + d−1 ancilla per row/column)',
)
