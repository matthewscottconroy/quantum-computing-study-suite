"""Question: cc_width"""
from core.models import Question

QUESTION = Question(
    id='cc_width',
    section='Create circuits',
    question='What does this print?\n\n```python\nfrom qiskit import QuantumCircuit\n\nqc = QuantumCircuit(3, 2)\nprint(qc.width())\n```',
    options=[
        '5',
        '3',
        '2',
        '6',
    ],
    correct_index=0,
    explanation='width() returns the total number of qubits plus classical bits: 3 + 2 = 5. Use num_qubits for just the quantum wires.',
    difficulty='easy',
)
