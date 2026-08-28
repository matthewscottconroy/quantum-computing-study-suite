"""Card: qk_qasm3_features"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qk_qasm3_features',
    category='Qiskit API',
    front='What does OpenQASM 3 add over OpenQASM 2?',
    back="Typed classical data (int, float, bit[n], bool), real-time control flow (if/else, for, while) on measurement results, subroutines/def, input/output parameters, and timing (delay, durations).  QASM 2 only had gates, measure, reset and a limited 'if'.",
)
