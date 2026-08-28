"""Question: qo_operator_shape"""
from core.models import Question

QUESTION = Question(
    id='qo_operator_shape',
    section='Quantum operations',
    question='What does this print?\n\n```python\nfrom qiskit import QuantumCircuit\nfrom qiskit.quantum_info import Operator\n\nqc = QuantumCircuit(2)\nqc.h(0)\nqc.cx(0, 1)\nprint(Operator(qc).data.shape)\n```',
    options=[
        '(4, 4)',
        '(2, 2)',
        '(4,)',
        '(8, 8)',
    ],
    correct_index=0,
    explanation='Operator(qc) builds the full unitary matrix of the circuit. A 2-qubit unitary acts on a 2² = 4-dimensional space, so the matrix is 4×4. A shape of (4,) would be a statevector, not an operator.',
    difficulty='easy',
)
