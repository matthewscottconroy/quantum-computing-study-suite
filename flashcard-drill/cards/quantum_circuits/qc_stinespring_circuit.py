"""Card: qc_stinespring_circuit"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qc_stinespring_circuit',
    category='Quantum Circuits',
    front='Quantum channel as a circuit',
    back='Any CPTP map ε(ρ) = Tr_E[U(ρ⊗|0⟩⟨0|_E)U†] — every channel has a unitary extension (Stinespring dilation) acting on system + environment ancilla.',
)
