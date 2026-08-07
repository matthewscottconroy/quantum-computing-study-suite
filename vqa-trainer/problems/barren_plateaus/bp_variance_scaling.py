"""Problem: bp_variance_scaling"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='bp_variance_scaling',
    category='Barren Plateaus',
    difficulty='intermediate',
    question='For a random n-qubit circuit forming an approximate 2-design, how does the variance of a gradient component ∂C/∂θ scale with n for a global cost function?',
    choices=[
        'Var[∂C/∂θ] ∝ 2^{-n} — exponentially small',
        'Var[∂C/∂θ] ∝ 1/n — polynomially small',
        'Var[∂C/∂θ] ∝ n² — grows with system size',
        'Var[∂C/∂θ] = constant — independent of n',
    ],
    correct_index=0,
    explanation='The key result of McClean et al. (2018): for random circuits and global cost functions, E[∂C/∂θ] = 0 and Var[∂C/∂θ] ≤ 2^{-n} (with exact expression depending on circuit architecture). The exponential suppression arises because random circuits produce states that are close to maximally mixed on any subsystem, and the cost function gradient concentrates exponentially tightly around zero.',
    hints=[
        'The variance of the gradient is the quantity that tells you if you can detect a gradient signal.',
    ],
    grade_mode=GradeMode.MC,
)
