"""Question: qo_pauli_evolve_clifford"""
from core.models import Question

QUESTION = Question(
    id='qo_pauli_evolve_clifford',
    section='Quantum operations',
    question='What does this print?\n\n```python\nfrom qiskit import QuantumCircuit\nfrom qiskit.quantum_info import Pauli\n\nqc = QuantumCircuit(1)\nqc.h(0)\nprint(Pauli("Z").evolve(qc))\n```',
    options=[
        'X — Pauli.evolve conjugates the operator, and H maps Z to X',
        'Z — evolve() applies the circuit to a state, leaving the operator unchanged',
        '-Z — H maps Z to −Z',
        'QiskitError — evolve() requires a Clifford, not a QuantumCircuit',
    ],
    correct_index=0,
    explanation="Pauli.evolve(circuit) performs Heisenberg-picture conjugation U†PU (use frame='s' for the Schrödinger convention UPU†), so it returns another Pauli whenever the circuit is Clifford — here HZH = X. It accepts a QuantumCircuit, a Clifford or another Pauli. Evolving a STATE is Statevector.evolve; confusing the two is why people expect a state back.",
    difficulty='hard',
)
