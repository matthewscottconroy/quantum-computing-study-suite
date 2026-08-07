"""Problem: qaoa_maxcut_eigenvalue"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='qaoa_maxcut_eigenvalue',
    category='QAOA',
    difficulty='intermediate',
    question='For the MaxCut cost Hamiltonian C = Σ_{(u,v)∈E} (1-ZᵤZᵥ)/2, what is the eigenvalue of C_{uv} = (1-ZᵤZᵥ)/2 when edge (u,v) is cut (nodes assigned to opposite sides)?',
    choices=[
        '1',
        '0',
        '1/2',
        '-1',
    ],
    correct_index=0,
    explanation='When nodes u and v are on opposite sides of the cut, their Z eigenvalues are opposite: Zᵤ = +1 and Zᵥ = -1 (or vice versa), so ZᵤZᵥ = -1. Therefore C_{uv} = (1-(-1))/2 = 1. When the edge is not cut, Zᵤ = Zᵥ, so ZᵤZᵥ = +1 and C_{uv} = 0. The total cost C counts the number of cut edges.',
    hints=[
        'Evaluate ZᵤZᵥ when the two nodes have opposite spin assignments.',
    ],
    grade_mode=GradeMode.MC,
)
