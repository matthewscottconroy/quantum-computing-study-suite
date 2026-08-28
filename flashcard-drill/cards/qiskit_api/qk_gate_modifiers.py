"""Card: qk_gate_modifiers"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qk_gate_modifiers',
    category='Qiskit API',
    front='Gate modifiers .control(n) and .power(k) — what do they do?',
    back='gate.control(n) returns the n-controlled version (XGate().control(2) → ccx).  gate.power(k) returns gate^k (SGate().power(2) → a phase gate = Z).  A whole circuit can be converted with qc.to_gate().control(1).',
)
