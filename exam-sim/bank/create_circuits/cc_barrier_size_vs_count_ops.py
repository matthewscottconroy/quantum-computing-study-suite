"""Question: cc_barrier_size_vs_count_ops"""
from core.models import Question

QUESTION = Question(
    id='cc_barrier_size_vs_count_ops',
    section='Create circuits',
    question='What does this print?\n\n```python\nfrom qiskit import QuantumCircuit\n\nqc = QuantumCircuit(3)\nqc.h(0)\nqc.barrier(0, 1)\nqc.h(1)\nqc.h(2)\nprint(qc.size(), dict(qc.count_ops()), qc.depth())\n```',
    options=[
        "3 {'h': 3, 'barrier': 1} 2",
        "4 {'h': 3, 'barrier': 1} 3",
        "3 {'h': 3} 2",
        "4 {'h': 3, 'barrier': 1} 2",
    ],
    correct_index=0,
    explanation='count_ops() lists every instruction, barriers included, but size() counts only real operations and skips directives — hence 3 vs a dict containing barrier. The barrier spans qubits 0 and 1 only, so h(1) is pushed to layer 2 while h(2) stays in layer 1: depth 2.',
    difficulty='hard',
)
