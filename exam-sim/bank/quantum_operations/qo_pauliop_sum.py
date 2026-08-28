"""Question: qo_pauliop_sum"""
from core.models import Question

QUESTION = Question(
    id='qo_pauliop_sum',
    section='Quantum operations',
    question='What is the value of `op` after this code?\n\n```python\nfrom qiskit.quantum_info import SparsePauliOp\n\nop = SparsePauliOp("Z") + SparsePauliOp("X")\n```',
    options=[
        "SparsePauliOp(['Z', 'X'], coeffs=[1.+0.j, 1.+0.j])",
        "A single Pauli 'ZX' acting on two qubits",
        'It raises an error — Pauli operators cannot be added, only composed',
        'The 2x2 matrix Z@X = iY as a SparsePauliOp',
    ],
    correct_index=0,
    explanation="Adding SparsePauliOps builds a linear combination (a sum of Pauli terms with coefficients) on the same number of qubits — exactly how Hamiltonians like H = Z + X are written. Tensoring ('ZX' on two qubits) would use ^ or .tensor(), and matrix multiplication would use @ or .compose().",
    difficulty='medium',
)
