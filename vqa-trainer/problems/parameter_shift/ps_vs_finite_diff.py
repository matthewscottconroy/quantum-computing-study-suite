"""Problem: ps_vs_finite_diff"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ps_vs_finite_diff',
    category='Parameter Shift',
    difficulty='intermediate',
    question='Compared to central finite differences, the parameter shift rule is advantageous because:',
    choices=[
        'It is exact (no approximation error), not just an O(ε²) approximation',
        'It requires only 1 circuit evaluation instead of 2',
        'It works for non-differentiable cost functions',
        'It has zero variance regardless of shot count',
    ],
    correct_index=0,
    explanation='Finite differences: [f(θ+ε) - f(θ-ε)]/(2ε) has O(ε²) truncation error and numerical instability for small ε. Parameter shift rule gives the exact gradient with shifts exactly ±π/2 — no approximation error, same number of circuit evaluations.',
    hints=[
        'The shift π/2 is exact, not a small approximation.',
    ],
    grade_mode=GradeMode.MC,
)
