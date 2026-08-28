"""Question: qo_h_matrix"""
from core.models import Question

QUESTION = Question(
    id='qo_h_matrix',
    section='Quantum operations',
    question='Which matrix represents the Hadamard gate?',
    options=[
        '1/√2 · [[1, 1], [1, -1]]',
        '1/√2 · [[1, -1], [1, 1]]',
        '[[0, 1], [1, 0]]',
        '1/√2 · [[1, 1], [1, 1]]',
    ],
    correct_index=0,
    explanation='H = 1/√2 [[1,1],[1,−1]] maps |0⟩ to |+⟩ and |1⟩ to |−⟩. [[0,1],[1,0]] is X, and the matrix with all +1 entries is not unitary at all.',
    difficulty='easy',
)
