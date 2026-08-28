"""Card: qk_measure_all"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qk_measure_all',
    category='Qiskit API',
    front='measure_all() vs measure(q, c) — what does each add?',
    back="measure_all() inserts a barrier then adds a NEW ClassicalRegister named 'meas' measuring every qubit (add_bits=False reuses existing clbits, no new register).  measure(q, c) maps one qubit to one existing clbit explicitly.",
)
