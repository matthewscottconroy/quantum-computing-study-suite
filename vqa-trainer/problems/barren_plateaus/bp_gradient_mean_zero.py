"""Problem: bp_gradient_mean_zero"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='bp_gradient_mean_zero',
    category='Barren Plateaus',
    difficulty='beginner',
    question='For a random parameterised quantum circuit, what is the expected value of a gradient component E[∂C/∂θ]?',
    choices=[
        '0 — the gradient has zero mean, not just small variance (the barren plateau problem is about variance, not bias)',
        '2^{-n} — exponentially small but nonzero',
        '1/p where p is the number of parameters',
        'The mean equals the gradient variance',
    ],
    correct_index=0,
    explanation='By symmetry of the Haar measure (random circuits), E[∂C/∂θ] = 0 for any cost function that is traceless (zero mean eigenvalue). The barren plateau phenomenon is specifically about the variance: Var[∂C/∂θ] ∝ 2^{-n}. The gradient is not just biased toward zero — it is exactly zero in expectation but exponentially concentrated around zero. This means gradient estimates are useless: they are centred at zero and have exponentially small fluctuations, making all parameter directions indistinguishable.',
    hints=[
        'The mean is exactly zero; the barren plateau problem is about the variance, not the mean.',
    ],
    grade_mode=GradeMode.MC,
)
