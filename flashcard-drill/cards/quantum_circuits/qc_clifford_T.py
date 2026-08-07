"""Card: qc_clifford_T"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qc_clifford_T',
    category='Quantum Circuits',
    front='Clifford + T gate set: why is it universal?',
    back='{H, S, CNOT, T} is universal: Clifford group provides all Pauli rotations and CNOT; T gate breaks out of Clifford group to achieve universality.',
)
