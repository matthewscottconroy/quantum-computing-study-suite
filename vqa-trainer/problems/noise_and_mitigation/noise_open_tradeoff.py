"""Problem: noise_open_tradeoff"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='noise_open_tradeoff',
    category='Noise & Mitigation',
    difficulty='advanced',
    question='Explain in 3–5 sentences: why does error mitigation (e.g. ZNE, PEC) come at an increased sampling overhead, and what determines the magnitude of this overhead?',
    choices=[],
    correct_index=-1,
    explanation='Error mitigation estimates the noiseless expectation value without physically correcting errors. To recover the signal, multiple circuits are run and combined — the quasi-probability weights or extrapolation coefficients can be large, amplifying statistical fluctuations. For PEC, the overhead is γ² = (Σᵢ|cᵢ|)² per circuit, which grows exponentially with the number of noisy gates. ZNE overhead is set by the condition number of the extrapolation matrix. The fundamental limit: noise mitigation trades bias for variance.',
    hints=[
        'Fewer systematic errors, but more shots needed — why?',
    ],
    grade_mode=GradeMode.CLAUDE,
)
