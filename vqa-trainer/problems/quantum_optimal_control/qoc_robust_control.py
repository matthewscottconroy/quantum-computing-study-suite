"""Problem: qoc_robust_control"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='qoc_robust_control',
    category='Optimal Control',
    difficulty='intermediate',
    question="What is 'robust' quantum optimal control?",
    choices=[
        'Optimising control pulses to achieve high fidelity averaged over a distribution of uncertainties (e.g. qubit frequency fluctuations, pulse amplitude errors), trading peak fidelity for robustness to noise',
        'Applying error correction codes to the control pulses to protect against pulse imperfections',
        'Running GRAPE multiple times with different random initialisations and selecting the most robust solution',
        'Designing control pulses that are robust to the barren plateau problem during optimisation',
    ],
    correct_index=0,
    explanation='Robust optimal control (Skinner et al. 2010; Motzoi et al. 2009) modifies the objective function: instead of maximising F(u, ξ₀) at a fixed parameter ξ₀, maximise ⟨F(u, ξ)⟩_ξ averaged over a distribution p(ξ) of uncertainties (e.g. qubit frequency drifts, coupling strength variations). GRAPE variants implement this by sampling {ξᵢ} and averaging gradients. Robust pulses are shorter and flatter than their nominal counterparts but maintain high fidelity across the uncertainty range — essential for day-to-day hardware operation where exact system parameters drift.',
    hints=[
        'Robustness = high fidelity over a distribution of uncertainties, not just one setting.',
    ],
    grade_mode=GradeMode.MC,
)
