"""Question: qo_compose_front"""
from core.models import Question

QUESTION = Question(
    id='qo_compose_front',
    section='Quantum operations',
    question='`h` and `z` are single-qubit Operators. Which expression equals the matrix product H·Z (that is, Z applied to the state FIRST)?\n\n```python\nfrom qiskit.quantum_info import Operator\n\nh = Operator.from_label("H")\nz = Operator.from_label("Z")\n```',
    options=[
        'h.compose(z, front=True)',
        'h.compose(z)',
        'h.tensor(z)',
        'h.expand(z)',
    ],
    correct_index=0,
    explanation="By default `h.compose(z)` means 'z after h' and evaluates to Z·H. Passing front=True composes the argument onto the input side instead, giving H·Z — the same thing as z.compose(h) or the matmul form h @ z. tensor() and expand() build a two-qubit 4 × 4 operator rather than a product on one qubit.",
    difficulty='hard',
)
