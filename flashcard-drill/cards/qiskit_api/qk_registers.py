"""Card: qk_registers"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qk_registers',
    category='Qiskit API',
    front='How are named quantum/classical registers created and used?',
    back="qr = QuantumRegister(2, 'q0'); cr = ClassicalRegister(2, 'c0'); qc = QuantumCircuit(qr, cr).  Registers group bits under a name; qc.qregs / qc.cregs list them.  Sampler results are keyed by classical-register name.",
)
