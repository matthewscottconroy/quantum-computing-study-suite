"""Problem: qaoa_approximation_ratio"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='qaoa_approximation_ratio',
    category='QAOA',
    difficulty='intermediate',
    question='For MaxCut on 3-regular graphs, the p=1 QAOA has an analytically proven approximation ratio of approximately:',
    choices=[
        '0.6924',
        '0.878 (Goemans-Williamson)',
        '0.5',
        '1.0 (exact)',
    ],
    correct_index=0,
    explanation='Farhi et al. (2014) proved QAOA p=1 achieves approximation ratio 0.6924 for MaxCut on 3-regular graphs with optimal gamma/beta. This is below the classical SDP-based Goemans-Williamson bound of 0.878 and the optimal 1.0. Deeper QAOA (larger p) approaches 1.0.',
    hints=[
        'p=1 QAOA is provably bounded below the classical SDP.',
    ],
    grade_mode=GradeMode.MC,
)
