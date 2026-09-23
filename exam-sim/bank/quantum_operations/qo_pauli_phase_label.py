"""Question: qo_pauli_phase_label"""
from core.models import Question

QUESTION = Question(
    id='qo_pauli_phase_label',
    section='Quantum operations',
    question='Which label is accepted by `Pauli(...)` in Qiskit 2.x?\n\n```python\nfrom qiskit.quantum_info import Pauli\n```',
    options=[
        "Pauli('-iY') — labels may carry an optional ±1/±i phase prefix",
        "Pauli('2X') — any complex coefficient may prefix the label",
        "Pauli('XY + ZZ') — sums of terms are allowed in a single label",
        "Pauli('X0 Z1') — qubit indices may be attached to each factor",
    ],
    correct_index=0,
    explanation="A Pauli label is an optional phase prefix from {+, -, +i, -i, i} followed by characters drawn from IXYZ, one per qubit, written little-endian. Arbitrary numeric coefficients, sums and index-annotated terms belong to SparsePauliOp instead (`SparsePauliOp.from_list([('XY', 1), ('ZZ', 1)])` or `from_sparse_list([('X', [0], 2)], num_qubits=n)`). The phase is kept in the group-phase exponent `Pauli.phase`, not folded into the matrix data.",
    difficulty='medium',
)
