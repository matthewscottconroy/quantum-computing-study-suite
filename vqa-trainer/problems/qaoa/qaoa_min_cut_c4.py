"""Problem: qaoa_min_cut_c4"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='qaoa_min_cut_c4',
    category='QAOA',
    difficulty='beginner',
    question='What is the minimum cut of a 4-node cycle graph C₄ (nodes 0-1-2-3-0 forming a square)?',
    choices=[
        '2',
        '4',
        '1',
        '3',
    ],
    correct_index=0,
    explanation='A min cut divides the 4 nodes into two sets to sever the fewest edges. Placing nodes {0,1} vs {2,3} cuts edges (1,2) and (3,0) — exactly 2 edges. Any bipartition of a 4-cycle graph severs at least 2 edges (the cycle has no bridge). The max cut of C₄ is 4 (alternate nodes: {0,2} vs {1,3} cuts all 4 edges).',
    hints=[
        'Try partitioning: {0,1} vs {2,3}. How many edges cross?',
    ],
    grade_mode=GradeMode.MC,
)
