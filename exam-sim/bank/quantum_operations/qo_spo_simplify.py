"""Question: qo_spo_simplify"""
from core.models import Question

QUESTION = Question(
    id='qo_spo_simplify',
    section='Quantum operations',
    question='What does this print?\n\n```python\nfrom qiskit.quantum_info import SparsePauliOp\n\nop = SparsePauliOp(["Z", "Z", "X"], coeffs=[1, -1, 2])\nprint(op.simplify().to_list())\n```',
    options=[
        "[('X', (2+0j))] — identical Pauli terms are summed and zero-coefficient terms are dropped",
        "[('Z', 0j), ('X', (2+0j))] — simplify() sums duplicates but keeps zero terms",
        "[('Z', (1+0j)), ('Z', (-1+0j)), ('X', (2+0j))] — simplify() only sorts, it never combines terms",
        "[('ZZX', (2+0j))] — simplify() concatenates the Pauli labels",
    ],
    correct_index=0,
    explanation='simplify() collects repeated Pauli strings by adding their coefficients and then removes any term whose coefficient falls below the tolerance, so +1·Z and −1·Z cancel completely and only 2·X survives. It never changes the number of qubits, and `chop()` is the related helper that only discards small coefficients without combining duplicates.',
    difficulty='medium',
)
