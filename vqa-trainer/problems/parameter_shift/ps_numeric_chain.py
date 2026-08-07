"""Problem: ps_numeric_chain"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ps_numeric_chain',
    category='Parameter Shift',
    difficulty='advanced',
    question='A circuit has two parameters θ₁ and θ₂. The cost is C(θ₁, θ₂) = sin(θ₁)cos(θ₂). Using the parameter shift rule, compute ∂C/∂θ₁ at (θ₁, θ₂) = (π/6, π/4).\n\nEnter your numeric answer to 4 decimal places.',
    choices=[],
    correct_index=-1,
    correct_value=0.6124,
    tolerance=0.001,
    explanation='∂C/∂θ₁ = cos(θ₁)cos(θ₂).\nAt (π/6, π/4): cos(π/6)·cos(π/4) = (√3/2)·(1/√2) = √3/(2√2) = √6/4 ≈ 0.6124',
    hints=[
        'Differentiate sin(θ₁) w.r.t. θ₁; treat cos(θ₂) as a constant.',
    ],
    grade_mode=GradeMode.AUTO,
)
