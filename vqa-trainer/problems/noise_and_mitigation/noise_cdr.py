"""Problem: noise_cdr"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='noise_cdr',
    category='Noise & Mitigation',
    difficulty='intermediate',
    question='What is Clifford Data Regression (CDR) for error mitigation?',
    choices=[
        'Train a regression model on Clifford circuits (classically simulable, similar noise) to learn the noisy-to-noiseless mapping, then apply to the target circuit',
        'Use classical data from previous experiments to correct the readout calibration matrix',
        'Decompose all gates into Clifford gates and correct non-Clifford corrections classically',
        'Regress the noise-amplified ZNE data using Clifford group statistics',
    ],
    correct_index=0,
    explanation="CDR (Czarnik et al. 2021) generates a training set by replacing non-Clifford gates in the target circuit with nearby Clifford gates, producing circuits that: (1) can be classically simulated to give noiseless reference values, and (2) share the same noise structure as the target circuit. A regression model f: ⟨O⟩_noisy → ⟨O⟩_noiseless is trained on this data, then applied to the real (non-Clifford) circuit's noisy measurement. CDR requires no noise model and can outperform ZNE for structured noise.",
    hints=[
        "Clifford circuits are classically simulable — that's key to getting noiseless training labels.",
    ],
    grade_mode=GradeMode.MC,
)
