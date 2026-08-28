"""Card: qk_partial_trace"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qk_partial_trace',
    category='Qiskit API',
    front='partial_trace(state, qargs) — what does qargs mean and what is returned?',
    back='qargs lists the qubits to TRACE OUT (discard).  Returns a DensityMatrix even when given a Statevector.  Tracing one qubit of a Bell state gives the maximally mixed single-qubit state, purity 0.5.',
)
