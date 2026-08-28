"""Question: cc_inverse"""
from core.models import Question

QUESTION = Question(
    id='cc_inverse',
    section='Create circuits',
    question='What is the single instruction inside `inv`?\n\n```python\nfrom qiskit import QuantumCircuit\n\nqc = QuantumCircuit(1)\nqc.s(0)\ninv = qc.inverse()\n```',
    options=[
        'sdg (S-dagger)',
        's — S is its own inverse',
        'z — because S² = Z',
        't — the square root of S',
    ],
    correct_index=0,
    explanation='inverse() replaces each gate with its adjoint in reverse order. S is not Hermitian (S² = Z, not I), so its inverse is S† (sdg). ',
    difficulty='medium',
)
