"""Question: cc_repeat_size"""
from core.models import Question

QUESTION = Question(
    id='cc_repeat_size',
    section='Create circuits',
    question='What does this print?\n\n```python\nfrom qiskit import QuantumCircuit\n\nqc = QuantumCircuit(1)\nqc.h(0)\nqc.x(0)\nrep = qc.repeat(3)\nprint(rep.size(), rep.decompose().size())\n```',
    options=[
        '3 6',
        '6 6',
        '6 12',
        '3 3',
    ],
    correct_index=0,
    explanation='repeat(n) appends the circuit to itself n times, but each copy is wrapped as a single composite instruction — so size() is 3, not 6. One decompose() unwraps those three wrappers into the underlying h and x pairs, giving 6 instructions. The circuit stays 1 qubit wide; repeat() never widens a circuit.',
    difficulty='easy',
)
