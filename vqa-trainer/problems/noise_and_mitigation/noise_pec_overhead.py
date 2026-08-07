"""Problem: noise_pec_overhead"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='noise_pec_overhead',
    category='Noise & Mitigation',
    difficulty='advanced',
    question='For Probabilistic Error Cancellation (PEC), the ideal gate is decomposed as ε_ideal = Σᵢ cᵢ εᵢ where γ = Σᵢ|cᵢ|. What is the sampling overhead relative to an unmitigated circuit?',
    choices=[
        'γ² — requires γ² times as many shots to achieve the same statistical precision',
        'γ — linear in the 1-norm of the quasi-probability coefficients',
        '2^γ — exponential in γ',
        'γ/2 — the overhead is halved because half the samples carry negative weight',
    ],
    correct_index=0,
    explanation='PEC uses importance sampling over the quasi-probability distribution {cᵢ/γ}. Each sample is a circuit drawn from |cᵢ|/γ, run, then its result is multiplied by γ·sign(cᵢ). The variance of each corrected sample is γ² times larger than the unmitigated variance, so γ² times more shots are needed to reach the same standard error. For n-gate circuits with per-gate overhead γ_g, the total overhead is γ² = (Π_gates γ_g)² — exponential in the number of gates.',
    hints=[
        'Variance of an importance-sampled estimator scales as the squared 1-norm of the weights.',
    ],
    grade_mode=GradeMode.MC,
)
