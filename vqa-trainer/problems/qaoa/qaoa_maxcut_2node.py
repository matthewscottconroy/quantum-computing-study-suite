"""Problem: qaoa_maxcut_2node"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='qaoa_maxcut_2node',
    category='QAOA',
    difficulty='intermediate',
    question='For a 2-node graph with one edge (u,v), the MaxCut cost Hamiltonian is:',
    choices=[
        'C = (1 - ZᵤZᵥ)/2',
        'C = ZᵤZᵥ',
        'C = Xᵤ ⊗ Xᵥ',
        'C = (Zᵤ + Zᵥ)/2',
    ],
    correct_index=0,
    explanation='For edge (u,v): C_{uv} = (1 - ZᵤZᵥ)/2 gives 1 if u,v are in different sets (ZᵤZᵥ = -1) and 0 if same (ZᵤZᵥ = +1). The full cost is the sum over all edges.',
    hints=[
        'Evaluate C when Zᵤ = +1,Zᵥ = -1 (cut edge) vs Zᵤ = Zᵥ = +1 (uncut).',
    ],
    grade_mode=GradeMode.MC,
)
