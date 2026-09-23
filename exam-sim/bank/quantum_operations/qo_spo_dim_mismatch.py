"""Question: qo_spo_dim_mismatch"""
from core.models import Question

QUESTION = Question(
    id='qo_spo_dim_mismatch',
    section='Quantum operations',
    question='What happens here?\n\n```python\nfrom qiskit.quantum_info import SparsePauliOp\n\nop = SparsePauliOp("X") + SparsePauliOp("XY")\n```',
    options=[
        'QiskitError — addition requires operators on the same number of qubits',
        "It succeeds — the 1-qubit term is padded with identities to 'IX'",
        "It succeeds and returns a 3-qubit operator labelled 'XXY'",
        'It succeeds but only after calling .simplify() on the result',
    ],
    correct_index=0,
    explanation="`+` is a linear combination of terms on one shared register, so the operands must have identical widths; mixing a 1-qubit and a 2-qubit operator raises QiskitError about mismatched dimensions. Qiskit never pads silently — write SparsePauliOp('IX') explicitly, or use `SparsePauliOp.from_sparse_list([('X', [0], 1)], num_qubits=2)`. Widening operands is what `tensor`/`expand` and `apply_layout` are for.",
    difficulty='medium',
)
