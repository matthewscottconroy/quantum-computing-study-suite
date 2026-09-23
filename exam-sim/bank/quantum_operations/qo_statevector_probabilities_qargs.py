"""Question: qo_statevector_probabilities_qargs"""
from core.models import Question

QUESTION = Question(
    id='qo_statevector_probabilities_qargs',
    section='Quantum operations',
    question='What does this print?\n\n```python\nfrom qiskit import QuantumCircuit\nfrom qiskit.quantum_info import Statevector\n\nqc = QuantumCircuit(2)\nqc.h(0)\nsv = Statevector(qc)\nprint(sv.probabilities([0]), sv.probabilities([1]))\n```',
    options=[
        '[0.5 0.5] [1. 0.] — qargs lists the qubits to KEEP, and only qubit 0 was put in superposition',
        '[1. 0.] [0.5 0.5] — qargs indexes the bitstring from the left',
        '[0.5 0.5] [0.5 0.5] — marginals of an unentangled state are always uniform',
        '[0.5 0. 0. 0.5] [0.5 0. 0. 0.5] — qargs is ignored and the full distribution is returned',
    ],
    correct_index=0,
    explanation='Statevector.probabilities(qargs) marginalizes onto the listed qubits — the opposite convention from partial_trace, whose qargs are traced OUT. H on qubit 0 gives that qubit a 50/50 marginal while qubit 1 stays deterministically |0⟩. probabilities_dict(qargs=[1]) gives the same numbers keyed by bitstring.',
    difficulty='medium',
)
