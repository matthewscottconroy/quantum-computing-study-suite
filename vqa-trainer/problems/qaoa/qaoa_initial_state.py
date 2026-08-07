"""Problem: qaoa_initial_state"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='qaoa_initial_state',
    category='QAOA',
    difficulty='beginner',
    question='The standard initial state for QAOA is:',
    choices=[
        '|+⟩^⊗n = H^⊗n|0⟩^⊗n — equal superposition of all bitstrings',
        '|0⟩^⊗n — all zeros',
        '|GHZ⟩ — maximally entangled state',
        'The ground state of U_B',
    ],
    correct_index=0,
    explanation='|+⟩^⊗n is the ground state of the mixer B = Σᵢ Xᵢ and puts equal weight on all 2ⁿ candidate solutions, allowing U_C to selectively amplify good solutions.',
    hints=[
        "It's the ground state of the standard mixer Hamiltonian.",
    ],
    grade_mode=GradeMode.MC,
)
