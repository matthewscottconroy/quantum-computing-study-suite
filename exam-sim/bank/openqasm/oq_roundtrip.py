"""Question: oq_roundtrip"""
from core.models import Question

QUESTION = Question(
    id='oq_roundtrip',
    section='OpenQASM',
    question='What does this print?\n\n```python\nfrom qiskit import QuantumCircuit, qasm3\n\nqc = QuantumCircuit(2)\nqc.h(0)\nqc.cx(0, 1)\nrebuilt = qasm3.loads(qasm3.dumps(qc))\nprint(rebuilt.num_qubits, dict(rebuilt.count_ops()))\n```',
    options=[
        "2 {'h': 1, 'cx': 1}",
        '2 {} — loads() returns an empty template circuit',
        'It raises an error — dumps() output is not guaranteed to be parseable',
        "4 {'h': 1, 'cx': 1} — the export doubles the register",
    ],
    correct_index=0,
    explanation='Serializing to OpenQASM 3 and parsing it back reconstructs an equivalent circuit: same 2-qubit register, same h and cx gates. dumps/loads are designed to round-trip standard circuits.',
    difficulty='medium',
)
