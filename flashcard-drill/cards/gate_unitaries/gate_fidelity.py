"""Card: gate_fidelity"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='gate_fidelity',
    category='Gate Unitaries',
    front='Gate fidelity F(U, V) = ?',
    back='F(U, V) = |Tr(U†V)|² / d²  where d is the Hilbert space dimension.  Equals 1 iff U = V (up to global phase).',
)
