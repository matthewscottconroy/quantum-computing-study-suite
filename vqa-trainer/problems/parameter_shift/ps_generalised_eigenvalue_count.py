"""Problem: ps_generalised_eigenvalue_count"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ps_generalised_eigenvalue_count',
    category='Parameter Shift',
    difficulty='advanced',
    question='For a gate with generator eigenvalues {0, ½, 1} (three distinct values), how many terms appear in the generalised parameter shift rule for ∂⟨H⟩/∂θ?',
    choices=[
        '3 terms — one per distinct eigenvalue gap (frequencies 0, ½, 1)',
        '2 terms — only the outermost eigenvalues matter',
        '6 terms — one for each pair of eigenvalues',
        '1 term — the rule always reduces to two circuit evaluations',
    ],
    correct_index=0,
    explanation='For a generator with d distinct eigenvalues, the expectation value ⟨H⟩(θ) is a trigonometric polynomial with d-1 distinct frequencies given by the pairwise eigenvalue differences. The generalised parameter shift rule (Schuld et al. 2021) has one term per frequency, requiring 2(d-1) circuit evaluations for the gradient. With eigenvalues {0, ½, 1}, the gaps are {½, 1} (2 non-zero frequencies), so the rule has 2 non-trivial terms (plus potentially a zero-frequency term) — in practice 3 terms in the generalised formula with shifts determined by each gap.',
    hints=[
        'Count the distinct non-zero eigenvalue differences (frequency components).',
    ],
    grade_mode=GradeMode.MC,
)
