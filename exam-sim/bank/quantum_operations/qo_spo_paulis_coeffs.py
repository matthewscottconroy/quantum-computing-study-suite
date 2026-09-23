"""Question: qo_spo_paulis_coeffs"""
from core.models import Question

QUESTION = Question(
    id='qo_spo_paulis_coeffs',
    section='Quantum operations',
    question='What does this print?\n\n```python\nfrom qiskit.quantum_info import SparsePauliOp\n\nH = SparsePauliOp(["II", "ZZ", "XX"], coeffs=[0.5, -1.0, 0.25])\nprint(len(H), H.paulis[1], H.coeffs[2])\n```',
    options=[
        '3 ZZ (0.25+0j) — .paulis is a PauliList of the terms and .coeffs a complex NumPy array',
        '3 -1.0 ZZ — .paulis holds the coefficients and .coeffs the labels',
        "2 ZZ (0.25+0j) — the identity term 'II' is not stored",
        '6 ZZ 0.25 — len() counts qubits across all terms',
    ],
    correct_index=0,
    explanation="A SparsePauliOp is a PauliList (`.paulis`) paired with a complex coefficient array (`.coeffs`), indexed together, so element 1 is 'ZZ' and coefficient 2 is 0.25 (printed as a complex number). len(H) and H.size both give the number of terms — 3, including the identity term, which is kept because it contributes a constant energy offset.",
    difficulty='easy',
)
