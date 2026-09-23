"""Question: cc_depth_two_qubit_filter"""
from core.models import Question

QUESTION = Question(
    id='cc_depth_two_qubit_filter',
    section='Create circuits',
    question='What does this print?\n\n```python\nfrom qiskit import QuantumCircuit\n\nqc = QuantumCircuit(3)\nqc.h(0)\nqc.h(1)\nqc.h(2)\nqc.cx(0, 1)\nqc.cx(1, 2)\nqc.x(0)\nprint(qc.depth(), qc.depth(lambda instr: len(instr.qubits) == 2))\n```',
    options=[
        '3 2',
        '3 3',
        '4 2',
        '6 2',
    ],
    correct_index=0,
    explanation='depth() accepts a filter function applied to each CircuitInstruction; only matching instructions contribute to the critical path. Full depth: [h,h,h] / [cx(0,1)] / [cx(1,2), x(0)] = 3. Counting only two-qubit gates, cx(0,1) and cx(1,2) share qubit 1 and so must be sequential: two-qubit depth 2 — the number a transpiler report cares about.',
    difficulty='hard',
)
