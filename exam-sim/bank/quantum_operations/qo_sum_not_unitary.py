"""Question: qo_sum_not_unitary"""
from core.models import Question

QUESTION = Question(
    id='qo_sum_not_unitary',
    section='Quantum operations',
    question='What does this print?\n\n```python\nfrom qiskit.quantum_info import SparsePauliOp\n\nprint(SparsePauliOp(["Z", "X"]).to_operator().is_unitary())\n```',
    options=[
        'False — Z + X has eigenvalues ±√2, so it is an observable, not a gate',
        'True — any sum of Pauli operators is unitary',
        'True — Z + X is the Hadamard gate',
        'QiskitError — is_unitary() is only defined for circuits',
    ],
    correct_index=0,
    explanation='Paulis are individually unitary, but their sums generally are not: Z + X has eigenvalues ±√2, so `is_unitary()` is False. Dividing by √2 gives exactly the Hadamard gate, which IS unitary. This is the difference between an observable you hand to an Estimator and an operation you append to a circuit — SparsePauliOp is built for the former.',
    difficulty='medium',
)
