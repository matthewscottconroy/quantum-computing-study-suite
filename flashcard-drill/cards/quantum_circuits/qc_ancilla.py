"""Card: qc_ancilla"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qc_ancilla',
    category='Quantum Circuits',
    front='Ancilla qubit: definition and use',
    back='Helper qubit initialised to |0⟩, used in intermediate computation, then uncomputed/reset.  Enables reversible implementation of irreversible functions.',
)
