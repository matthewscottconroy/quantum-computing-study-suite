"""Question: qo_s_squared"""
from core.models import Question

QUESTION = Question(
    id='qo_s_squared',
    section='Quantum operations',
    question='Applying the S gate twice in a row to the same qubit is equivalent to which single gate?',
    options=[
        'Z',
        'X',
        'T',
        'Identity',
    ],
    correct_index=0,
    explanation='S = diag(1, i) is the square root of Z: S² = diag(1, i²) = diag(1, −1) = Z. It is not self-inverse, so the answer is not the identity.',
    difficulty='easy',
)
