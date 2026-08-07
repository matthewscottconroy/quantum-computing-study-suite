"""Problem: noise_fundamental_limit_mitigation"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='noise_fundamental_limit_mitigation',
    category='Noise & Mitigation',
    difficulty='advanced',
    question='What is the fundamental limit of error mitigation without error correction (Takagi et al. 2022)?',
    choices=[
        'The sampling overhead of any error mitigation protocol grows exponentially in the number of noisy gates T and per-gate noise rate ε: overhead ≥ e^{Ω(Tε)}',
        'Error mitigation can reduce the effective error rate to zero given enough circuit shots',
        'The overhead of error mitigation scales polynomially with qubit count but exponentially with circuit depth',
        'No fundamental limit exists — error mitigation can in principle achieve zero systematic error',
    ],
    correct_index=0,
    explanation='Takagi, Endo, Zhao & Gu (2022) proved a fundamental lower bound: for any error mitigation protocol that achieves ε-accuracy on circuits with T noisy gates, the required sampling overhead N_samples is at least e^{Ω(Tε_noise)} where ε_noise is the per-gate noise rate. This is exponential in the circuit volume T·ε_noise. For a 100-gate circuit at 1% error, overhead ≥ e^{Ω(1)} ≈ 3× minimum; for 1000-gate circuit, overhead ≥ e^{Ω(10)} ≈ 22,000×. This result establishes that error mitigation (without correction) cannot scale to arbitrary circuit depths — fault tolerance remains essential for large circuits.',
    hints=[
        'The lower bound involves both the number of gates and the per-gate error rate.',
    ],
    grade_mode=GradeMode.MC,
)
