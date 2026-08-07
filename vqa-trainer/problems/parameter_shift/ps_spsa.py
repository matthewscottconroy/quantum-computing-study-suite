"""Problem: ps_spsa"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ps_spsa',
    category='Parameter Shift',
    difficulty='intermediate',
    question='SPSA (Simultaneous Perturbation Stochastic Approximation) estimates the gradient with how many circuit evaluations per step, regardless of the number of parameters?',
    choices=[
        '2',
        'p (one per parameter)',
        '4',
        '2p',
    ],
    correct_index=0,
    explanation='SPSA simultaneously perturbs all p parameters by a random ±1 vector Δ: ∂C/∂θᵢ ≈ [C(θ+cΔ) - C(θ-cΔ)] / (2cΔᵢ). Only 2 circuit evaluations are needed regardless of p, making SPSA very efficient for circuits with hundreds of parameters. The trade-off is a noisy gradient estimate that requires more optimisation steps to converge than the exact parameter shift gradient.',
    hints=[
        'SPSA perturbs all parameters simultaneously — so the number of evaluations is constant.',
    ],
    grade_mode=GradeMode.MC,
)
