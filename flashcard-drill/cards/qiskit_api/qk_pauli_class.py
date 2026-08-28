"""Card: qk_pauli_class"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qk_pauli_class',
    category='Qiskit API',
    front="What algebra does quantum_info's Pauli class support?",
    back="Multi-qubit Pauli labels like Pauli('XZ'), with phase tracking: Pauli('X') @ Pauli('Z') = -iY.  Methods: compose, tensor, commutes, anticommutes (X and Z anticommute), evolve.  Group structure is exact including ±1, ±i phases.",
)
