"""Problem: ps_numeric_sin"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ps_numeric_sin',
    category='Parameter Shift',
    difficulty='intermediate',
    question='For a single-qubit circuit ⟨Z⟩(θ) = cos(θ), compute ∂⟨Z⟩/∂θ using the parameter shift rule at θ = π/3.\n\nUse the formula with shifts ±π/2. Give your answer to 4 decimal places.',
    choices=[],
    correct_index=-1,
    correct_value=-0.866,
    tolerance=0.001,
    explanation='⟨Z⟩(θ+π/2) = cos(θ+π/2) = -sin(θ)\n⟨Z⟩(θ-π/2) = cos(θ-π/2) = +sin(θ)\nGradient = [-sin(θ) - sin(θ)] / 2 = -sin(θ)\nAt θ=π/3: -sin(π/3) = -√3/2 ≈ -0.866',
    hints=[
        'cos(θ ± π/2) = ∓sin(θ).',
    ],
    grade_mode=GradeMode.AUTO,
)
