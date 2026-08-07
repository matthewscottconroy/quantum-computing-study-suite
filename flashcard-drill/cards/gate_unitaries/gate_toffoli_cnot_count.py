"""Card: gate_toffoli_cnot_count"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='gate_toffoli_cnot_count',
    category='Gate Unitaries',
    front='CNOT count for Toffoli gate',
    back='Toffoli requires 6 CNOTs in general; with a single clean ancilla, only 3 CNOTs are needed.  The ancilla-free 6-CNOT decomposition is optimal.',
)
