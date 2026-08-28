"""Question: qo_swap_decomp"""
from core.models import Question

QUESTION = Question(
    id='qo_swap_decomp',
    section='Quantum operations',
    question='When a SWAP gate is decomposed into CX gates (e.g. by transpiling to a basis of cx and single-qubit gates), how many CX gates does it require?',
    options=[
        '3',
        '2',
        '1',
        '4',
    ],
    correct_index=0,
    explanation='SWAP = CX(0,1)·CX(1,0)·CX(0,1): three alternating CNOTs. This is why routing on limited-connectivity hardware is expensive — every inserted SWAP costs three entangling gates.',
    difficulty='medium',
)
