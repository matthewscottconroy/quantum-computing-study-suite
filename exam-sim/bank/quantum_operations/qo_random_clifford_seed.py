"""Question: qo_random_clifford_seed"""
from core.models import Question

QUESTION = Question(
    id='qo_random_clifford_seed',
    section='Quantum operations',
    question='What does this print?\n\n```python\nfrom qiskit.quantum_info import random_clifford\n\na = random_clifford(2, seed=42)\nb = random_clifford(2, seed=42)\nprint(type(a).__name__, a == b)\n```',
    options=[
        'Clifford True — random_clifford samples the Clifford group and the seed makes it reproducible',
        'QuantumCircuit True — random_clifford returns a circuit, not a tableau',
        'Clifford False — the seed only fixes the qubit count, not the sampled element',
        'Operator True — random_clifford returns a unitary matrix',
    ],
    correct_index=0,
    explanation='random_clifford(num_qubits, seed=...) draws uniformly from the n-qubit Clifford group and returns a Clifford (tableau) object; passing the same integer seed reproduces the same element, which is what makes randomized-benchmarking and mirror-circuit experiments repeatable. Call `.to_circuit()` for a QuantumCircuit or `.to_operator()` for the unitary.',
    difficulty='easy',
)
