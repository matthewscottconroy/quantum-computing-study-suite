"""Problem: ps_numeric_gradient"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ps_numeric_gradient',
    category='Parameter Shift',
    difficulty='intermediate',
    question='Given ⟨H⟩(θ + π/2) = 0.3 and ⟨H⟩(θ - π/2) = -0.7, compute ∂⟨H⟩/∂θ using the parameter shift rule.\n\nEnter your numeric answer (exact decimal).',
    choices=[],
    correct_index=-1,
    correct_value=0.5,
    tolerance=0.0001,
    explanation='∂⟨H⟩/∂θ = [⟨H⟩(θ+π/2) - ⟨H⟩(θ-π/2)] / 2 = [0.3 - (-0.7)] / 2 = 1.0 / 2 = 0.5',
    hints=[
        'Subtract the two values and divide by 2.',
    ],
    grade_mode=GradeMode.AUTO,
)
