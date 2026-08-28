"""Question: qo_sxsdg"""
from core.models import Question

QUESTION = Question(
    id='qo_sxsdg',
    section='Quantum operations',
    question='Up to global phase, what is the result of conjugating X by the S gate, i.e. the sequence S·X·S† (applied right to left)?\n\n```python\nqc = QuantumCircuit(1)\nqc.sdg(0)\nqc.x(0)\nqc.s(0)\n```',
    options=[
        'Y',
        'X',
        'Z',
        'H',
    ],
    correct_index=0,
    explanation='S rotates the Bloch sphere by 90° about the Z axis, mapping the X axis onto the Y axis. Conjugation S·X·S† therefore turns X into Y. (Note the circuit applies sdg first because circuits compose left-to-right while operators compose right-to-left.)',
    difficulty='hard',
)
