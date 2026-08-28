"""Card: qk_qasm_includes"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qk_qasm_includes',
    category='Qiskit API',
    front='Which standard include file does each OpenQASM version use?',
    back='OPENQASM 2.0 → include "qelib1.inc";  OPENQASM 3.0 → include "stdgates.inc";  These define the standard gate library (h, x, cx, rz, …) that Qiskit\'s exporters emit by default.',
)
