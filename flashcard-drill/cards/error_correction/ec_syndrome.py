"""Card: ec_syndrome"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='ec_syndrome',
    category='Error Correction',
    front='How does syndrome measurement work?',
    back='Ancilla qubit coupled to data qubits via controlled-Pauli; ancilla measured in Z basis.  Result identifies error type and location without reading the logical state.',
)
