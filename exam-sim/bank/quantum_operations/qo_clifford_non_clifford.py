"""Question: qo_clifford_non_clifford"""
from core.models import Question

QUESTION = Question(
    id='qo_clifford_non_clifford',
    section='Quantum operations',
    question='What happens here?\n\n```python\nfrom qiskit import QuantumCircuit\nfrom qiskit.quantum_info import Clifford\n\nqc = QuantumCircuit(1)\nqc.h(0)\nqc.t(0)\ncl = Clifford(qc)\n```',
    options=[
        'QiskitError — T is not a Clifford gate, so the tableau cannot be built',
        'It succeeds — Clifford approximates any circuit to the nearest stabilizer operation',
        'It succeeds — T is a Clifford gate because it is diagonal',
        'TranspilerError — the circuit must first be transpiled to a Clifford basis',
    ],
    correct_index=0,
    explanation="Clifford stores a stabilizer tableau, which can only represent operations that map Paulis to Paulis. H, S, X, Y, Z, CX, CZ and SWAP qualify; T (a π/4 phase) does not, so the constructor raises QiskitError('Cannot update Clifford with non-Clifford gate t'). There is no silent approximation, and transpiling cannot turn a T into Cliffords exactly.",
    difficulty='medium',
)
