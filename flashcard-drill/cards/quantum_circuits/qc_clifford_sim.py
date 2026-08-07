"""Card: qc_clifford_sim"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qc_clifford_sim',
    category='Quantum Circuits',
    front='Clifford circuit simulation complexity',
    back="Clifford circuits on n qubits can be simulated in O(n²) space and O(n) time per gate using the Heisenberg representation of Pauli operators — Gottesman's algorithm.",
)
