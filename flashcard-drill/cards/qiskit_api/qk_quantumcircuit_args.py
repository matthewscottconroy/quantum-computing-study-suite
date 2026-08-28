"""Card: qk_quantumcircuit_args"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qk_quantumcircuit_args',
    category='Qiskit API',
    front='QuantumCircuit(3, 2) — what do the two arguments mean?',
    back='3 qubits and 2 classical bits.  Positional args are (num_qubits, num_clbits); you can instead pass QuantumRegister/ClassicalRegister objects.  qc.num_qubits and qc.num_clbits report the totals.',
)
