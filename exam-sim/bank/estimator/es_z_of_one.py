"""Question: es_z_of_one"""
from core.models import Question

QUESTION = Question(
    id='es_z_of_one',
    section='Estimator',
    question='What does this print (rounded)?\n\n```python\nfrom qiskit import QuantumCircuit\nfrom qiskit.primitives import StatevectorEstimator\nfrom qiskit.quantum_info import SparsePauliOp\n\nqc = QuantumCircuit(1)\nqc.x(0)\nest = StatevectorEstimator()\nev = est.run([(qc, SparsePauliOp("Z"))]).result()[0].data.evs\nprint(float(ev))\n```',
    options=[
        '-1.0',
        '1.0',
        '0.0',
        '0.5',
    ],
    correct_index=0,
    explanation='X flips the qubit to |1⟩, which is the Z eigenstate with eigenvalue −1, so ⟨Z⟩ = −1. +1 would be the value for |0⟩ and 0 for an equal superposition.',
    difficulty='easy',
)
