"""Problem: qaoa_open_graph_advantage"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='qaoa_open_graph_advantage',
    category='QAOA',
    difficulty='advanced',
    question='In 3–5 sentences, describe under what conditions (graph structure, problem type) you would expect QAOA to outperform the best classical algorithms.',
    choices=[],
    correct_index=-1,
    explanation='QAOA is most likely to outperform classical algorithms when: (1) the problem has long-range entanglement in the optimal solution that classical local search misses; (2) the graph has high girth or tree-like local structure (where p-local QAOA captures exact solution structure); (3) the problem is constrained and a feasibility-preserving mixer (QAOA+) avoids the exponential infeasible-space overhead that classical penalty methods incur. For MaxCut on 3-regular graphs at p≥11, QAOA is conjectured to exceed the Goemans-Williamson 0.878 ratio (conditionally on the Unique Games Conjecture being tight). Dense problems and problems with polynomial classical algorithms are unlikely candidates for quantum advantage.',
    hints=[
        'Consider locality, constraint structure, and known classical algorithm bounds.',
    ],
    grade_mode=GradeMode.CLAUDE,
)
