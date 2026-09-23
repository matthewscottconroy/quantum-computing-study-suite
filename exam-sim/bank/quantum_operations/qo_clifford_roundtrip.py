"""Question: qo_clifford_roundtrip"""
from core.models import Question

QUESTION = Question(
    id='qo_clifford_roundtrip',
    section='Quantum operations',
    question='What does this print?\n\n```python\nfrom qiskit.quantum_info import Clifford, random_clifford\n\ncl = random_clifford(3, seed=5)\nqc = cl.to_circuit()\nprint(type(qc).__name__, Clifford(qc) == cl)\n```',
    options=[
        'QuantumCircuit True — to_circuit() synthesizes a circuit with exactly the same tableau',
        'QuantumCircuit False — synthesis only reproduces the tableau up to a random Pauli',
        'Clifford True — to_circuit() returns another Clifford wrapper',
        'Instruction True — to_circuit() returns an opaque instruction, not a circuit',
    ],
    correct_index=0,
    explanation="Clifford.to_circuit() runs stabilizer synthesis and returns a real QuantumCircuit over H/S/CX-style gates whose tableau round-trips exactly, so Clifford(qc) == cl. Note that the tableau does not track global phase, so the synthesized circuit's Operator may differ from an original circuit's by a phase — compare those with .equiv(), not ==.",
    difficulty='hard',
)
