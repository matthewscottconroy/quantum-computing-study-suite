"""Card: gate_CNOT_from_CZ"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='gate_CNOT_from_CZ',
    category='Gate Unitaries',
    front='CNOT in terms of CZ and Hadamard',
    back='CNOT = (I⊗H) · CZ · (I⊗H) — apply H to target before and after CZ.  Conversely, CZ = (I⊗H) · CNOT · (I⊗H).',
)
