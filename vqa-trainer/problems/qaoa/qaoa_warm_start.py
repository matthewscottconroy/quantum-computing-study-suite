"""Problem: qaoa_warm_start"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='qaoa_warm_start',
    category='QAOA',
    difficulty='advanced',
    question="What is the main benefit of 'warm-starting' QAOA with a classical relaxation solution?",
    choices=[
        'The initial state encodes problem structure, requiring fewer QAOA layers for good solutions',
        'It eliminates the need for the mixer unitary',
        'It guarantees the optimal solution at p=1',
        'It reduces the number of Pauli terms in the cost Hamiltonian',
    ],
    correct_index=0,
    explanation='Warm-start QAOA initialises the quantum state from a classical relaxation (e.g. SDP relaxation), encoding approximate problem structure into the amplitudes. The QAOA circuit then refines this solution rather than starting from a uniform superposition. This can reduce the required QAOA depth p significantly.',
    hints=[
        'A good initial point makes the quantum optimisation task easier.',
    ],
    grade_mode=GradeMode.MC,
)
