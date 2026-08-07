"""Card: hw_josephson"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='hw_josephson',
    category='Quantum Hardware',
    front='Josephson junction: role in superconducting qubits',
    back='Nonlinear inductor with inductance L_J = Φ₀/(2πIc cos(φ)).  Its nonlinearity creates an anharmonic spectrum, making the two lowest levels an addressable qubit.',
)
