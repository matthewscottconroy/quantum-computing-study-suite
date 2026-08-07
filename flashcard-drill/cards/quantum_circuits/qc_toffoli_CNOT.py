"""Card: qc_toffoli_CNOT"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qc_toffoli_CNOT',
    category='Quantum Circuits',
    front='CNOT count to implement an n-qubit Toffoli?',
    back='O(n) CNOTs using ancilla qubits; without ancilla: O(n²) — multiple constructions exist depending on ancilla availability',
)
