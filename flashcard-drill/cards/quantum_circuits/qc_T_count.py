"""Card: qc_T_count"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qc_T_count',
    category='Quantum Circuits',
    front='T-count: what is it and why does it matter?',
    back='Number of T (π/8) gates in a circuit.  Each T requires magic state distillation in fault-tolerant computing — the dominant resource overhead.',
)
