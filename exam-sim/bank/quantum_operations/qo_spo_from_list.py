"""Question: qo_spo_from_list"""
from core.models import Question

QUESTION = Question(
    id='qo_spo_from_list',
    section='Quantum operations',
    question='What does this print?\n\n```python\nfrom qiskit.quantum_info import SparsePauliOp\n\nH = SparsePauliOp.from_list([("ZZ", 0.5), ("XX", -1.2)])\nprint(H.num_qubits, len(H), H.coeffs[1])\n```',
    options=[
        '2 2 (-1.2+0j) — two qubits, two terms, and coefficients are stored as complex numbers',
        '2 2 -1.2 — coefficients keep the float type they were given',
        '4 2 (-1.2+0j) — num_qubits counts the characters across all labels',
        '2 4 (-1.2+0j) — len() counts the Pauli characters, not the terms',
    ],
    correct_index=0,
    explanation="from_list takes (label, coefficient) pairs whose labels must all be the same width; that width is num_qubits (2), the number of pairs is len(H) (also H.size, 2), and coefficients are always stored in a complex128 array, so H.coeffs[1] prints as (-1.2+0j). Use from_sparse_list([('Z', [0], 0.5)], num_qubits=n) when you would rather not spell out the identities.",
    difficulty='easy',
)
