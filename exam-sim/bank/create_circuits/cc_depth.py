"""Question: cc_depth"""
from core.models import Question

QUESTION = Question(
    id='cc_depth',
    section='Create circuits',
    question='What does this print?\n\n```python\nfrom qiskit import QuantumCircuit\n\nqc = QuantumCircuit(3)\nqc.h(0)\nqc.cx(0, 1)\nqc.cx(1, 2)\nqc.x(0)\nprint(qc.depth())\n```',
    options=[
        '3',
        '4',
        '2',
        '1',
    ],
    correct_index=0,
    explanation='Depth is the number of parallel layers on the critical path. Layer 1: h(0). Layer 2: cx(0,1). Layer 3: cx(1,2) and x(0) can run simultaneously (disjoint qubits), so depth is 3 — not 4, which is the gate count (size()).',
    difficulty='medium',
)
