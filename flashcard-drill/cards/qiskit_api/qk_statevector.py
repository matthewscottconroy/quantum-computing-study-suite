"""Card: qk_statevector"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qk_statevector',
    category='Qiskit API',
    front='Three ways to build/evolve a Statevector in qiskit.quantum_info?',
    back="Statevector.from_label('01') (leftmost char = highest qubit, so '01' = |q1=0, q0=1⟩ = index 1); Statevector(qc) simulates a circuit from |0…0⟩; sv.evolve(qc) applies a circuit/operator to an existing state.",
)
