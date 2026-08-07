"""Problem: ps_spsa_variance_scaling"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ps_spsa_variance_scaling',
    category='Parameter Shift',
    difficulty='intermediate',
    question='For SPSA with N random perturbation directions accumulated before a parameter update, how does the variance of the gradient estimate scale with N?',
    choices=[
        'Var ∝ 1/N — variance decreases inversely with the number of accumulated perturbations',
        'Var ∝ 1/√N — standard square-root improvement from averaging',
        'Var ∝ N — variance increases with more perturbations due to accumulation of Bernoulli noise',
        'Var is constant — independent of N since all perturbations share the same random seed',
    ],
    correct_index=0,
    explanation='Averaging N independent SPSA gradient estimates reduces variance by the standard law of large numbers: Var[mean of N i.i.d. estimates] = σ²/N. The variance of a single SPSA estimate σ² is O(p/c²) for step size c and p parameters (since the denominator Δᵢ is Bernoulli ±1, giving variance contribution per parameter). With N accumulated perturbations the estimate variance is σ²/N ∝ 1/N. Mini-batch SPSA (averaging multiple random directions per step) is one practical way to reduce noise at the cost of 2N circuit evaluations per step.',
    hints=[
        'Averaging i.i.d. estimates always reduces variance as 1/N — the standard result.',
    ],
    grade_mode=GradeMode.MC,
)
