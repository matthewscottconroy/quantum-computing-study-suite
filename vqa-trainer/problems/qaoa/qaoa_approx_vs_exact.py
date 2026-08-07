"""Problem: qaoa_approx_vs_exact"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='qaoa_approx_vs_exact',
    category='QAOA',
    difficulty='intermediate',
    question="What distinguishes QAOA as an 'approximate' optimisation algorithm vs an exact one?",
    choices=[
        'QAOA at finite depth p gives an approximation ratio < 1 for MaxCut — it is not guaranteed to find the optimal solution',
        'QAOA produces approximate eigenvalues of the cost Hamiltonian, not exact eigenstates',
        'The parameter optimisation is approximate because COBYLA is a derivative-free heuristic',
        'QAOA gives approximate results because the quantum hardware is noisy',
    ],
    correct_index=0,
    explanation='For finite p, QAOA achieves approximation ratio α_p = ⟨C⟩_p / C_opt < 1 for MaxCut on general graphs. For example, p=1 achieves α≈0.6924 on 3-regular graphs. The ratio improves as p grows but only reaches 1 in the p→∞ limit. QAOA is therefore a polynomial-time quantum heuristic that trades circuit depth (p) for solution quality (α_p), analogous to classical approximation algorithms like Goemans-Williamson (α=0.878) which also do not guarantee optimality.',
    hints=[
        'Approximation ratio is ⟨C⟩/C_opt, which is < 1 for finite p.',
    ],
    grade_mode=GradeMode.MC,
)
