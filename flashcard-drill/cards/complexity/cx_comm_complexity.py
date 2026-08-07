"""Card: cx_comm_complexity"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='cx_comm_complexity',
    category='Complexity',
    front='Quantum communication complexity advantage',
    back='Some communication problems require exponentially less quantum communication than classical.  Disjointness: O(√n) qubits quantumly vs Ω(n) classically.',
)
