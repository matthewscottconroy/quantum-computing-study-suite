"""Question: qo_spo_tensor_expand"""
from core.models import Question

QUESTION = Question(
    id='qo_spo_tensor_expand',
    section='Quantum operations',
    question='What does this print?\n\n```python\nfrom qiskit.quantum_info import SparsePauliOp\n\nprint(SparsePauliOp("X").tensor(SparsePauliOp("Z")).paulis[0],\n      SparsePauliOp("X").expand(SparsePauliOp("Z")).paulis[0])\n```',
    options=[
        'XZ ZX — tensor() puts the caller on the high qubits, expand() puts it on the low qubits',
        'ZX XZ — tensor() puts the caller on the low qubits',
        'XZ XZ — expand() is an alias for tensor()',
        'XX ZZ — the labels are broadcast, not concatenated',
    ],
    correct_index=0,
    explanation="`a.tensor(b)` builds a ⊗ b, so the caller's label is written on the LEFT of the combined label (high qubit indices); `a.expand(b)` builds b ⊗ a, putting the caller on the right (low indices). The infix `^` is the operator form of tensor. Since Qiskit reads Pauli labels little-endian, 'XZ' means Z on qubit 0 and X on qubit 1.",
    difficulty='medium',
)
