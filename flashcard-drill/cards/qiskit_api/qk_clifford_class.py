"""Card: qk_clifford_class"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qk_clifford_class',
    category='Qiskit API',
    front="What is quantum_info's Clifford class for?",
    back='Clifford(qc) converts a Clifford-only circuit (H, S, CX, Pauli…) to its symplectic tableau — a boolean table of how it maps X/Z generators.  Enables efficient classical simulation (Gottesman-Knill); to_circuit()/to_instruction() convert back.',
)
