"""Question: qo_hzh"""
from core.models import Question

QUESTION = Question(
    id='qo_hzh',
    section='Quantum operations',
    question='Up to global phase, the sequence H·Z·H applied to a single qubit is equivalent to which gate?\n\n```python\nqc = QuantumCircuit(1)\nqc.h(0)\nqc.z(0)\nqc.h(0)\n```',
    options=[
        'X',
        'Y',
        'Z',
        'Identity',
    ],
    correct_index=0,
    explanation='H maps the Z basis to the X basis, so conjugating Z by H yields X (HZH = X). This basis-change identity is why a Z-basis phase flip becomes a bit flip in the Hadamard basis.',
    difficulty='medium',
)
