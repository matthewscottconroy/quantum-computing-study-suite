"""Card: qc_two_qubit_count"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qc_two_qubit_count',
    category='Quantum Circuits',
    front='Two-qubit gate count for arbitrary n-qubit unitary?',
    back='O(4ⁿ) two-qubit gates required in general — unitary group SU(2ⁿ) has 4ⁿ−1 real degrees of freedom',
)
