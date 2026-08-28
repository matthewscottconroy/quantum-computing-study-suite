"""Question: cc_ctor_counts"""
from core.models import Question

QUESTION = Question(
    id='cc_ctor_counts',
    section='Create circuits',
    question='What do the following attributes evaluate to?\n\n```python\nfrom qiskit import QuantumCircuit\n\nqc = QuantumCircuit(3, 2)\nprint(qc.num_qubits, qc.num_clbits)\n```',
    options=[
        '3 2',
        '2 3',
        '3 3',
        '5 0',
    ],
    correct_index=0,
    explanation='QuantumCircuit(n, m) creates n qubits and m classical bits, so num_qubits is 3 and num_clbits is 2. The first constructor argument is always the qubit count.',
    difficulty='easy',
)
