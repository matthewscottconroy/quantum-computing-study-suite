"""Problem: ps_numeric_basic"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ps_numeric_basic',
    category='Parameter Shift',
    difficulty='intermediate',
    question='Given ⟨H⟩(θ = π/4 + π/2) = 0.6  and  ⟨H⟩(θ = π/4 - π/2) = -0.2, compute ∂⟨H⟩/∂θ at θ = π/4 using the parameter shift rule.\n\nEnter your numeric answer (exact decimal).',
    choices=[],
    correct_index=-1,
    correct_value=0.4,
    tolerance=0.0001,
    explanation='∂⟨H⟩/∂θ = [0.6 - (-0.2)] / 2 = 0.8 / 2 = 0.4',
    hints=[
        'Subtract the two energy values and divide by 2.',
    ],
    grade_mode=GradeMode.AUTO,
)
