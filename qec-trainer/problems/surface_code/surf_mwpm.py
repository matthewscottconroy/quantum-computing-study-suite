"""Problem: surf_mwpm"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='surf_mwpm',
    category='Surface Code',
    difficulty='advanced',
    question='The standard classical decoding algorithm for the surface code is:',
    choices=[
        'Minimum Weight Perfect Matching (MWPM)',
        'Maximum Likelihood Decoding',
        'Viterbi algorithm',
        'Union-Find decoder',
    ],
    correct_index=0,
    explanation='MWPM (Blossom algorithm) finds the minimum weight pairing of syndrome defects. It runs in O(n³) but fast implementations exist. Union-Find is faster but slightly suboptimal.',
    hints=[
        'Think of syndrome defects as vertices to be matched in pairs.',
    ],
    grade_mode=GradeMode.AUTO,
)
