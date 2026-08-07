"""Problem: ps_numeric_shift_answer"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ps_numeric_shift_answer',
    category='Parameter Shift',
    difficulty='intermediate',
    question='Given ⟨H⟩(θ + π/2) = -0.5 and ⟨H⟩(θ - π/2) = 0.3, compute ∂⟨H⟩/∂θ using the parameter shift rule.\n\nEnter your numeric answer (exact decimal).',
    choices=[],
    correct_index=-1,
    correct_value=-0.4,
    tolerance=0.0001,
    explanation='∂⟨H⟩/∂θ = [⟨H⟩(θ+π/2) - ⟨H⟩(θ-π/2)] / 2 = [-0.5 - 0.3] / 2 = -0.8 / 2 = -0.4',
    hints=[
        'Subtract the two energy values and divide by 2. Watch the sign.',
    ],
    grade_mode=GradeMode.AUTO,
)
