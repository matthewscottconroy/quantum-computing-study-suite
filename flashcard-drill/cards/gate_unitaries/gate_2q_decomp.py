"""Card: gate_2q_decomp"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='gate_2q_decomp',
    category='Gate Unitaries',
    front='Maximum CNOT count to decompose any 2-qubit unitary',
    back='Any 2-qubit unitary can be decomposed into at most 3 CNOT gates plus single-qubit rotations.  This bound is tight — some unitaries genuinely require 3 CNOTs.',
)
