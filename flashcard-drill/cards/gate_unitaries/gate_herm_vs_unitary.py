"""Card: gate_herm_vs_unitary"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='gate_herm_vs_unitary',
    category='Gate Unitaries',
    front='Hermitian gate vs unitary gate: difference?',
    back='Hermitian: U†=U (observable, self-inverse up to spectrum).  Unitary: U†U=I (valid quantum gate).  Pauli gates are both.',
)
