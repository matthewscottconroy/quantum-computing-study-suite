"""Problem: noise_clifford_data_regression"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='noise_clifford_data_regression',
    category='Noise & Mitigation',
    difficulty='advanced',
    question='How does Clifford Data Regression (CDR) work as an error mitigation technique?',
    choices=[
        'Generates near-Clifford training circuits (classically simulable for reference values), trains a regression model mapping noisy→noiseless, applies it to the non-Clifford target circuit',
        'Uses Clifford group symmetries to decompose the target circuit into classically simulable components',
        'Trains a regression model on ZNE-extrapolated data points using Clifford circuit statistics as prior',
        'Replaces non-Clifford gates with their nearest Clifford approximations and corrects the energy classically',
    ],
    correct_index=0,
    explanation="CDR (Czarnik et al. 2021): (1) Take the target non-Clifford circuit. (2) Replace non-Clifford gates (e.g. T gates, Rz with irrational angle) with random nearby Clifford gates, creating ~50–200 near-Clifford training circuits. (3) Classically simulate each to get the noiseless expectation value (training label). (4) Run each on the noisy device to get the noisy value (training feature). (5) Fit a regression f(⟨O⟩_noisy) ≈ ⟨O⟩_noiseless on this data. (6) Apply f to the real target circuit's noisy measurement. CDR requires no noise model and automatically captures complex noise correlations.",
    hints=[
        "Near-Clifford circuits are classically simulable — that's where the training labels come from.",
    ],
    grade_mode=GradeMode.MC,
)
