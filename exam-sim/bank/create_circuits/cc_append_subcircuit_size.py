"""Question: cc_append_subcircuit_size"""
from core.models import Question

QUESTION = Question(
    id='cc_append_subcircuit_size',
    section='Create circuits',
    question='What does this print?\n\n```python\nfrom qiskit import QuantumCircuit\n\nsub = QuantumCircuit(2, name="bell")\nsub.h(0)\nsub.cx(0, 1)\n\nqc = QuantumCircuit(4)\nqc.append(sub.to_gate(), [1, 3])\nprint(qc.size(), dict(qc.count_ops()))\n```',
    options=[
        "1 {'bell': 1}",
        "2 {'h': 1, 'cx': 1}",
        "2 {'bell': 2}",
        'It raises a CircuitError — a two-qubit gate cannot be appended to non-adjacent qubits',
    ],
    correct_index=0,
    explanation="append() inserts the converted circuit as ONE opaque instruction named after the sub-circuit, so size() is 1 and count_ops() reports {'bell': 1}. Qubit adjacency is irrelevant at circuit-construction time (it only matters after transpilation to a coupling map). Call qc.decompose() to inline the h and cx.",
    difficulty='medium',
)
