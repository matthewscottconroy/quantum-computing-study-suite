"""Card: qc_clifford_not_univ"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qc_clifford_not_univ',
    category='Quantum Circuits',
    front='Why is the Clifford group alone not universal?',
    back='Gottesman-Knill: Clifford circuits on stabilizer states are efficiently classically simulable — they cannot generate computational hardness without a non-Clifford gate like T.',
)
