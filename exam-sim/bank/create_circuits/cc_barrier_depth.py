"""Question: cc_barrier_depth"""
from core.models import Question

QUESTION = Question(
    id='cc_barrier_depth',
    section='Create circuits',
    question='What does this print?\n\n```python\nfrom qiskit import QuantumCircuit\n\nqc = QuantumCircuit(2)\nqc.h(0)\nqc.barrier()\nqc.h(1)\nprint(qc.depth())\n```',
    options=[
        '2 — the barrier prevents the two H gates from sharing a layer',
        '1 — the H gates act on different qubits, so they are parallel',
        '3 — the barrier counts as its own layer',
        '0 — barriers reset the depth counter',
    ],
    correct_index=0,
    explanation='Without the barrier the two H gates act on disjoint qubits and would form one layer (depth 1). A full barrier forces everything after it into later layers, so the depth becomes 2. Barriers themselves are not counted as gate layers.',
    difficulty='hard',
)
