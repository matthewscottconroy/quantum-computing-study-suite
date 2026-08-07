"""Problem: ps_second_derivative"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ps_second_derivative',
    category='Parameter Shift',
    difficulty='intermediate',
    question='Computing the second derivative ∂²⟨H⟩/∂θ² using the parameter shift rule requires how many circuit evaluations, and what is the formula?',
    choices=[
        '4 evaluations: [⟨H⟩(θ+π) - 2⟨H⟩(θ) + ⟨H⟩(θ-π)] / 4',
        '2 evaluations: same as the first derivative but divided by 2',
        '3 evaluations: finite-difference correction applied to the first-derivative shifts',
        '6 evaluations: three pairs of ±π/2 shifts at different centre points',
    ],
    correct_index=0,
    explanation='Applying the parameter shift rule twice yields the Hessian diagonal term. For a Pauli generator with shift s=π/2, applying the rule to ∂⟨H⟩/∂θ gives: ∂²⟨H⟩/∂θ² = [⟨H⟩(θ+π) - 2⟨H⟩(θ) + ⟨H⟩(θ-π)] / 4. This needs 3 distinct points (θ, θ+π, θ-π), so at minimum 3 evaluations, but if ⟨H⟩(θ) was already evaluated, only 2 additional evaluations are needed. The coefficients [1, -2, 1]/4 mirror the classical second finite-difference stencil, but here the result is exact, not an approximation.',
    hints=[
        'Apply the shift rule a second time to ∂⟨H⟩/∂θ, treating it as a new function of θ.',
    ],
    grade_mode=GradeMode.MC,
)
