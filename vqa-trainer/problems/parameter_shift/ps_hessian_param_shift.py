"""Problem: ps_hessian_param_shift"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ps_hessian_param_shift',
    category='Parameter Shift',
    difficulty='advanced',
    question='How is the Hessian ∂²C/∂θᵢ∂θⱼ (for i≠j) computed using the parameter shift rule, and how many circuit evaluations does it require?',
    choices=[
        'Apply the shift rule twice: shift θᵢ by ±π/2 and θⱼ by ±π/2, giving 4 evaluations per off-diagonal Hessian entry',
        'Apply the shift rule once per parameter: 2 evaluations using a combined shift (π/2, π/2) for both parameters simultaneously',
        'Compute the Hessian from the QFIM diagonal: 2p evaluations for all diagonal entries',
        'The Hessian cannot be computed exactly with the parameter shift rule — only finite differences apply',
    ],
    correct_index=0,
    explanation="The cross-derivative uses the shift rule twice: ∂²C/∂θᵢ∂θⱼ = [C(θᵢ+π/2,θⱼ+π/2) - C(θᵢ+π/2,θⱼ-π/2) - C(θᵢ-π/2,θⱼ+π/2) + C(θᵢ-π/2,θⱼ-π/2)] / 4. This requires 4 circuit evaluations per off-diagonal entry. The full p×p Hessian therefore needs O(p²) evaluations — the same cost as the QFIM. Diagonal entries need 3 evaluations each (as for second derivative). This exact Hessian enables Newton's method, which can converge in far fewer steps than gradient descent near the optimum, at the cost of O(p²) quantum evaluations.",
    hints=[
        'Shift both parameters independently — that gives a 2×2 grid of ±π/2 combinations.',
    ],
    grade_mode=GradeMode.MC,
)
