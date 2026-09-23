"""Question: qo_spo_compose_vs_dot"""
from core.models import Question

QUESTION = Question(
    id='qo_spo_compose_vs_dot',
    section='Quantum operations',
    question='What does this print?\n\n```python\nfrom qiskit.quantum_info import SparsePauliOp\n\na = SparsePauliOp("X").compose(SparsePauliOp("Y"))\nb = SparsePauliOp("X").dot(SparsePauliOp("Y"))\nprint(a.coeffs[0], b.coeffs[0])\n```',
    options=[
        '-1j 1j — compose() applies the argument AFTER the caller (Y·X), dot() applies it before (X·Y)',
        '1j 1j — compose() and dot() are aliases for the same product',
        '1j -1j — compose() is X·Y and dot() is Y·X',
        '-1j -1j — Pauli products always pick up a −i phase',
    ],
    correct_index=0,
    explanation="`A.compose(B)` means 'B acting after A', i.e. the matrix product B·A, so X.compose(Y) = Y·X = −iZ. `A.dot(B)` (also written `A @ B`) is the ordinary matrix product A·B = X·Y = +iZ. Getting these two backwards silently flips the sign of every non-commuting term in a Hamiltonian; `&` is the operator form of compose, `@` the operator form of dot.",
    difficulty='hard',
)
