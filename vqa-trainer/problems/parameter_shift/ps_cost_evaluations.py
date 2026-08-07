"""Problem: ps_cost_evaluations"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ps_cost_evaluations',
    category='Parameter Shift',
    difficulty='beginner',
    question='A VQA circuit has 50 parameters. How many circuit evaluations does one full gradient computation require using the parameter shift rule?',
    choices=[
        '100',
        '50',
        '25',
        '200',
    ],
    correct_index=0,
    explanation='Each of the 50 parameters needs 2 evaluations (θ+π/2 and θ-π/2). Total = 2 × 50 = 100. Compare to finite differences which also needs 2 per param but introduces approximation error.',
    hints=[
        '2 evaluations per parameter.',
    ],
    grade_mode=GradeMode.MC,
)
