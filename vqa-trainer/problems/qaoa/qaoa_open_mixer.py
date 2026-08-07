"""Problem: qaoa_open_mixer"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='qaoa_open_mixer',
    category='QAOA',
    difficulty='advanced',
    question='Explain in 3–5 sentences: why might you use a non-standard mixer in QAOA, and give one example of when this is beneficial.',
    choices=[],
    correct_index=-1,
    explanation='The standard X-mixer does not preserve problem constraints (e.g., feasibility in combinatorial problems). A non-standard mixer can be designed to explore only the feasible subspace, preventing wasteful steps into infeasible states. Example: for graph coloring with k colors, an XY-mixer (ij) swaps color assignments between nodes i and j, preserving the total number of each color. This reduces the effective search space and can improve convergence.',
    hints=[
        'Think about constrained optimisation problems where not all bitstrings are valid solutions.',
    ],
    grade_mode=GradeMode.CLAUDE,
)
