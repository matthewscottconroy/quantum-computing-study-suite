"""Question: cc_grover_operator"""
from core.models import Question

QUESTION = Question(
    id='cc_grover_operator',
    section='Create circuits',
    question='What does this print (to within floating-point noise)?\n\n```python\nfrom qiskit import QuantumCircuit\nfrom qiskit.circuit.library import grover_operator\nfrom qiskit.quantum_info import Statevector\n\noracle = QuantumCircuit(2)\noracle.cz(0, 1)\n\nqc = QuantumCircuit(2)\nqc.h([0, 1])\nqc.compose(grover_operator(oracle), inplace=True)\nprint(Statevector(qc).probabilities_dict())\n```',
    options=[
        "{'11': 1.0}, with the other three basis states at ~0",
        "{'00': 0.25, '01': 0.25, '10': 0.25, '11': 0.25} — one iteration cannot amplify anything",
        "{'00': 0.5, '11': 0.5}",
        "{'00': 1.0} — grover_operator() builds only the diffuser, not the oracle",
    ],
    correct_index=0,
    explanation='grover_operator(oracle) returns oracle followed by the zero-reflection diffuser. For a 2-qubit search with a single marked state, one Grover iteration is exactly enough: the marked state |11⟩ (the state the cz phase-flips) reaches probability 1. Note grover_operator() is the function form; the GroverOperator class is deprecated in Qiskit 2.1.',
    difficulty='hard',
)
