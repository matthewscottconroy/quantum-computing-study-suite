"""Question: qo_t_squared"""
from core.models import Question

QUESTION = Question(
    id='qo_t_squared',
    section='Quantum operations',
    question='What single gate is equivalent to two consecutive T gates?',
    options=[
        'S',
        'Z',
        'H',
        'Tdg',
    ],
    correct_index=0,
    explanation='T = diag(1, e^{iπ/4}) is the fourth root of Z; squaring it gives diag(1, e^{iπ/2}) = diag(1, i) = S. Four T gates would make a Z.',
    difficulty='easy',
)
