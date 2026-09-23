"""Question: cc_broadcast_qubit_list"""
from core.models import Question

QUESTION = Question(
    id='cc_broadcast_qubit_list',
    section='Create circuits',
    question='What does this print?\n\n```python\nfrom qiskit import QuantumCircuit\n\nqc = QuantumCircuit(3)\nqc.h(range(3))\nprint(qc.size(), qc.depth())\n```',
    options=[
        '3 1',
        '1 1',
        '3 3',
        'It raises a TypeError — gate methods take a single qubit index, not an iterable',
    ],
    correct_index=0,
    explanation='Gate methods broadcast over any iterable of qubits, so qc.h(range(3)) appends three separate H instructions (size 3). They act on disjoint qubits and therefore share one layer, so the depth is 1.',
    difficulty='easy',
)
