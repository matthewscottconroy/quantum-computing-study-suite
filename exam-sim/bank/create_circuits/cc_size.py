"""Question: cc_size"""
from core.models import Question

QUESTION = Question(
    id='cc_size',
    section='Create circuits',
    question='What does this print?\n\n```python\nfrom qiskit import QuantumCircuit\n\nqc = QuantumCircuit(2, 2)\nqc.h(0)\nqc.cx(0, 1)\nqc.measure([0, 1], [0, 1])\nprint(qc.size())\n```',
    options=[
        '4',
        '2',
        '3',
        '6',
    ],
    correct_index=0,
    explanation='size() counts every instruction, including the two measure operations: h + cx + measure + measure = 4. It is not the qubit count and not the depth.',
    difficulty='easy',
)
