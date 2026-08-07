"""Problem: bp_error_in_variables"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='bp_error_in_variables',
    category='Barren Plateaus',
    difficulty='advanced',
    question="What is the 'error-in-variables' model for noisy gradient estimation in VQAs?",
    choices=[
        'Treating shot noise as additive measurement noise on the gradient: g_measured = g_true + ε where ε ~ N(0,σ²/S) with S shots',
        'Modelling gate errors as small rotations applied to the true parameter values',
        'Accounting for readout errors by adding a bias term to the cost function gradient',
        'A Bayesian model where the true parameters are unknown and estimated from noisy circuit outputs',
    ],
    correct_index=0,
    explanation='In the error-in-variables framework, each gradient component is estimated as g_i = (C(θ+π/2) - C(θ-π/2))/2 from S shots. Shot noise contributes measurement variance σ²/S where σ² ≤ 1 (Pauli variance bound). In a barren plateau, the true gradient g_true ≈ 0 with variance 2^{-n}, so the measured gradient is dominated by shot noise ε — the signal-to-noise ratio is ~√(S·2^{-n}). To get SNR=1 requires S~2^n shots, making the gradient useless for optimisation regardless of which optimiser is used.',
    hints=[
        'Model the gradient estimate as true gradient plus measurement noise, then find the SNR.',
    ],
    grade_mode=GradeMode.MC,
)
