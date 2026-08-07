"""Card: qc_uncompute"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qc_uncompute',
    category='Quantum Circuits',
    front='Uncomputation: what is it?',
    back='Running the ancilla-preparation circuit in reverse to restore ancilla to |0⟩ after use — prevents entanglement between ancilla and output (garbage qubits)',
)
