"""Problem: qaoa_complete_graph_maxcut"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='qaoa_complete_graph_maxcut',
    category='QAOA',
    difficulty='intermediate',
    question='For the MaxCut problem on a complete graph Kₙ with n even, what is the maximum cut size?',
    choices=[
        'n²/4 — partition into two equal halves, each of size n/2, cutting all n/2 × n/2 edges between the halves',
        'n(n-1)/2 — the total number of edges in Kₙ',
        'n-1 — a spanning tree cut',
        '2n — two edges per node',
    ],
    correct_index=0,
    explanation='Kₙ has n(n-1)/2 total edges. For even n, the maximum cut partitions the n nodes into two sets of size n/2 each. All edges between the two sets are cut: (n/2)×(n/2) = n²/4 edges. The edges within each set (not cut) number 2×C(n/2,2) = n(n-2)/4. So MaxCut = n(n-1)/2 - n(n-2)/4 = n²/4. For example, K₄: MaxCut = 4, K₆: MaxCut = 9.',
    hints=[
        'Partition n nodes into two equal halves. How many edges cross the partition?',
    ],
    grade_mode=GradeMode.MC,
)
