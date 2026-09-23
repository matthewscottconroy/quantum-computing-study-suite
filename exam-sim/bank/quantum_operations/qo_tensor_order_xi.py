"""Question: qo_tensor_order_xi"""
from core.models import Question

QUESTION = Question(
    id='qo_tensor_order_xi',
    section='Quantum operations',
    question='What does this print?\n\n```python\nfrom qiskit.quantum_info import Operator, Statevector\n\nop = Operator.from_label("X").tensor(Operator.from_label("I"))\nprint(Statevector.from_label("00").evolve(op).probabilities_dict())\n```',
    options=[
        "{'10': 1.0} — a.tensor(b) puts `a` on the HIGHER qubits, so X lands on qubit 1",
        "{'01': 1.0} — the left operand of tensor() always acts on qubit 0",
        "{'00': 1.0} — X ⊗ I is the identity on a two-qubit register",
        'QiskitError — Operator.from_label only accepts multi-qubit labels',
    ],
    correct_index=0,
    explanation="In `a.tensor(b)` the caller `a` occupies the most-significant (highest-index) qubits and `b` the least-significant ones, matching Qiskit's little-endian Kronecker convention: X.tensor(I) is the operator labelled 'XI', which flips qubit 1 and leaves qubit 0 alone, so |00⟩ becomes |10⟩. Use `expand()` (or swap the operands) when you want the caller on the low qubits. Operator.from_label happily accepts multi-character labels such as 'XI'.",
    difficulty='medium',
)
