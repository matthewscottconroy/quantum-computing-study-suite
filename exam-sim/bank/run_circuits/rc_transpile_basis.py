"""Question: rc_transpile_basis"""
from core.models import Question

QUESTION = Question(
    id='rc_transpile_basis',
    section='Run circuits',
    question='What is true about `out`?\n\n```python\nfrom qiskit import QuantumCircuit, transpile\n\nqc = QuantumCircuit(2)\nqc.h(0)\nqc.cx(0, 1)\nout = transpile(qc, basis_gates=["sx", "rz", "cz"])\n```',
    options=[
        'It contains only sx, rz and cz gates; h and cx have been rewritten',
        'It is identical to qc — transpile only changes circuits when a backend is given',
        'It raises an error because cx cannot be expressed with cz',
        'It contains h and cx plus extra sx/rz gates',
    ],
    correct_index=0,
    explanation='transpile translates every gate into the requested basis: H becomes rz/sx sequences and CX becomes CZ conjugated by single-qubit gates. No backend is required for basis translation, and CX is straightforwardly expressible using CZ plus Hadamard-like rotations.',
    difficulty='medium',
)
