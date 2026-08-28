"""Card: qk_compose_vs_append"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qk_compose_vs_append',
    category='Qiskit API',
    front='qc.compose(other) vs qc.append(instr, qargs) — when to use which?',
    back='compose merges another whole circuit onto qc (returns a NEW circuit unless inplace=True; maps registers/bits automatically).  append adds a single Instruction/Gate onto the listed qubits, e.g. qc.append(QFT(2), [0, 1]).',
)
