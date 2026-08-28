"""Card: qk_little_endian"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qk_little_endian',
    category='Qiskit API',
    front='Qiskit bit ordering: X gate on qubit 0 of a 2-qubit circuit — which counts key?',
    back="'01' — Qiskit is LITTLE-ENDIAN: qubit 0 is the RIGHTMOST character of the bitstring and the least-significant bit (statevector index 1).  Same convention in Statevector labels and tensor products: |q1 q0⟩.",
)
