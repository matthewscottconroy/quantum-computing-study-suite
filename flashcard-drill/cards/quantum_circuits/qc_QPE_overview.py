"""Card: qc_QPE_overview"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qc_QPE_overview',
    category='Quantum Circuits',
    front='QPE circuit overview',
    back='n ancilla qubits in |+⟩, each controls U^{2ᵏ} acting on eigenstate register, then inverse QFT on ancilla — reads phase φ in binary to n-bit precision',
)
