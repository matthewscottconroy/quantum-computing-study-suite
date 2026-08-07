"""Problem: qaoa_open_vs_annealing"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='qaoa_open_vs_annealing',
    category='QAOA',
    difficulty='advanced',
    question='In 3–5 sentences, compare QAOA to classical simulated annealing: what are the structural similarities and the key differences?',
    choices=[],
    correct_index=-1,
    explanation="Similarities: both are iterative heuristics that explore an energy landscape; both start from an unbiased initial state and use a parameter schedule (β,γ or temperature) to guide exploration toward lower-energy solutions; both offer no worst-case guarantee. Differences: QAOA uses quantum superposition to evaluate many solutions simultaneously, while SA evaluates one classical configuration at a time. QAOA can exploit quantum tunnelling to escape local minima that trap SA. SA has a rigorous convergence guarantee for slow cooling (Gibbs distribution), while QAOA's convergence guarantees are mainly asymptotic (p→∞). QAOA also requires a quantum computer, whereas SA runs efficiently on classical hardware.",
    hints=[
        'Think about superposition and tunnelling as quantum analogues of thermal fluctuations.',
    ],
    grade_mode=GradeMode.CLAUDE,
)
