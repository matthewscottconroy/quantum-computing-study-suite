"""Question: cc_for_loop"""
from core.models import Question

QUESTION = Question(
    id='cc_for_loop',
    section='Create circuits',
    question='What does this print?\n\n```python\nfrom qiskit import QuantumCircuit\n\nqc = QuantumCircuit(1)\nwith qc.for_loop(range(3)):\n    qc.x(0)\nprint(dict(qc.count_ops()))\n```',
    options=[
        "{'for_loop': 1}",
        "{'x': 3}",
        "{'for_loop': 3}",
        "{'x': 1, 'for_loop': 1}",
    ],
    correct_index=0,
    explanation="for_loop() creates a single ForLoopOp whose body circuit holds one x gate; the loop is executed by the backend's control-flow support, not unrolled at build time. If you want three real x instructions in the outer circuit, write a plain Python `for` loop instead.",
    difficulty='medium',
)
