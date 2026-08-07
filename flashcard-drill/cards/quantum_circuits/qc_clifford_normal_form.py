"""Card: qc_clifford_normal_form"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qc_clifford_normal_form',
    category='Quantum Circuits',
    front='Clifford circuit normal form',
    back='Any Clifford circuit can be rewritten as: Hadamard layer → CNOT layer → single-qubit phase layer.  Enables canonical forms for circuit equivalence checking.',
)
