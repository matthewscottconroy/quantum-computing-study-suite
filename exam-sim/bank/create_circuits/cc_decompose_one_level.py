"""Question: cc_decompose_one_level"""
from core.models import Question

QUESTION = Question(
    id='cc_decompose_one_level',
    section='Create circuits',
    question='What does this print?\n\n```python\nfrom qiskit import QuantumCircuit\n\ninner = QuantumCircuit(2, name="inner")\ninner.h(0)\ninner.cx(0, 1)\n\nmid = QuantumCircuit(2, name="mid")\nmid.append(inner.to_gate(), [0, 1])\n\ntop = QuantumCircuit(2)\ntop.append(mid.to_gate(), [0, 1])\nprint(dict(top.decompose().count_ops()))\n```',
    options=[
        "{'inner': 1}",
        "{'h': 1, 'cx': 1}",
        "{'mid': 1}",
        "{'h': 1, 'cx': 1, 'inner': 1}",
    ],
    correct_index=0,
    explanation='decompose() expands exactly one level of the instruction hierarchy, turning the "mid" gate into its body — which is the still-opaque "inner" gate. Use decompose(reps=2) (or repeated decompose() calls, or transpile() with a basis) to keep unrolling down to h and cx.',
    difficulty='medium',
)
