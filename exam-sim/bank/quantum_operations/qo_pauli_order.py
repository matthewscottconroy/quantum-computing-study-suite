"""Question: qo_pauli_order"""
from core.models import Question

QUESTION = Question(
    id='qo_pauli_order',
    section='Quantum operations',
    question='What does this print?\n\n```python\nfrom qiskit import QuantumCircuit\nfrom qiskit.primitives import StatevectorEstimator\nfrom qiskit.quantum_info import SparsePauliOp\n\nqc = QuantumCircuit(2)\nqc.x(0)\nest = StatevectorEstimator()\nev = est.run([(qc, SparsePauliOp("IZ"))]).result()[0].data.evs\nprint(float(ev))\n```',
    options=[
        "-1.0 — in the string 'IZ' the rightmost character acts on qubit 0",
        "1.0 — 'IZ' applies Z to qubit 1, which is still |0⟩",
        '0.0 — |1⟩ is not an eigenstate of Z',
        "-1.0, but only because 'IZ' is automatically reversed to 'ZI'",
    ],
    correct_index=0,
    explanation="Qiskit Pauli strings are little-endian: the rightmost character of 'IZ' acts on qubit 0. Since qubit 0 is |1⟩ (a Z eigenstate with eigenvalue −1), ⟨IZ⟩ = −1. Assuming the leftmost character is qubit 0 (big-endian) is a classic mistake.",
    difficulty='hard',
)
