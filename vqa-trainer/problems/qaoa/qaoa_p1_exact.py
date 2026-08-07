"""Problem: qaoa_p1_exact"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='qaoa_p1_exact',
    category='QAOA',
    difficulty='advanced',
    question='For which graph structures is p=1 QAOA guaranteed to find the exact MaxCut solution?',
    choices=[
        'Graphs where the MaxCut is determined by local 1-hop neighbourhood structure, such as certain trees',
        'All 3-regular graphs',
        'Complete graphs (all-to-all connectivity)',
        'Bipartite graphs only',
    ],
    correct_index=0,
    explanation="At p=1, each qubit's effective evolution depends only on its immediate neighbours (the 1-local view). For graphs where the optimal cut assignment of every node is determined entirely by its 1-hop neighbourhood — such as specific tree graphs or triangle-free graphs — p=1 QAOA is sufficient to recover the exact solution. For general graphs (e.g. dense or highly symmetric ones), higher p is needed to capture the multi-hop correlations required for the optimal cut.",
    hints=[
        "At p=1, the QAOA evolution is local — it can only 'see' 1 hop away.",
    ],
    grade_mode=GradeMode.MC,
)
