"""Question: cc_tensor_order"""
from core.models import Question

QUESTION = Question(
    id='cc_tensor_order',
    section='Create circuits',
    question='Where do the two gates end up?\n\n```python\nfrom qiskit import QuantumCircuit\n\ntop = QuantumCircuit(1)\ntop.h(0)\nbottom = QuantumCircuit(1)\nbottom.x(0)\ntp = top.tensor(bottom)\n```',
    options=[
        'x on qubit 0 and h on qubit 1 — the argument takes the low-index qubits',
        'h on qubit 0 and x on qubit 1 — the caller takes the low-index qubits',
        'Both gates on qubit 0 of a 1-qubit circuit — tensor() only merges instructions',
        'A CircuitError — tensor() requires the two circuits to have different widths',
    ],
    correct_index=0,
    explanation="a.tensor(b) forms the Kronecker product a ⊗ b. In Qiskit's little-endian convention the right-hand operand occupies the least-significant (lowest-index) qubits, so `bottom`'s x lands on qubit 0 and `top`'s h lands on qubit 1. Use b.tensor(a) — or compose with an explicit qubits= mapping — if you want the opposite layout.",
    difficulty='hard',
)
