"""Card: gate_native_sets"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='gate_native_sets',
    category='Gate Unitaries',
    front='Native gate sets: superconducting vs trapped-ion',
    back='Superconducting: {CNOT (or CZ), Rz, SX (√X)}.  Trapped-ion: {MS (Mølmer-Sørensen), Ry, Rz}.  All other gates are compiled into these sets.',
)
