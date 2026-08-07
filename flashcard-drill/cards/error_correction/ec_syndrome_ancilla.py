"""Card: ec_syndrome_ancilla"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='ec_syndrome_ancilla',
    category='Error Correction',
    front='Syndrome measurement circuit',
    back='Ancilla prepared in |+⟩ for X-type stabilizers, |0⟩ for Z-type; CNOT chain couples ancilla to data qubits; ancilla measured.  Result (syndrome bit) reveals error type without revealing logical state.',
)
