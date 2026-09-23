"""Question: cc_num_nonlocal_gates"""
from core.models import Question

QUESTION = Question(
    id='cc_num_nonlocal_gates',
    section='Create circuits',
    question='What does this print?\n\n```python\nfrom qiskit import QuantumCircuit\n\nqc = QuantumCircuit(3)\nqc.h(0)\nqc.cx(0, 1)\nqc.ccx(0, 1, 2)\nqc.x(2)\nprint(qc.num_nonlocal_gates())\n```',
    options=[
        '2 — cx and ccx both act on more than one qubit',
        '1 — only the cx counts as non-local',
        '3 — every gate after the first h is non-local',
        '4 — num_nonlocal_gates() is an alias for size()',
    ],
    correct_index=0,
    explanation='num_nonlocal_gates() counts instructions acting on two or more qubits, so the cx and the ccx both count while h and x do not. It is the quick way to size up the entangling cost of a circuit; size() would report 4 and count_ops() the per-name breakdown.',
    difficulty='easy',
)
