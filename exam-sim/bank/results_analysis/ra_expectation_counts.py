"""Question: ra_expectation_counts"""
from core.models import Question

QUESTION = Question(
    id='ra_expectation_counts',
    section='Results analysis',
    question="A single qubit is measured in the computational basis over 1000 shots: {'0': 600, '1': 400}. What is the estimate of ⟨Z⟩?",
    options=[
        '0.2 — (600 − 400) / 1000',
        "0.6 — the probability of '0'",
        '-0.2 — (400 − 600) / 1000',
        '1.0 — Z eigenvalues are ±1 so the average is always ±1',
    ],
    correct_index=0,
    explanation='Outcome 0 contributes eigenvalue +1 and outcome 1 contributes −1, so ⟨Z⟩ ≈ (N₀ − N₁)/N = (600 − 400)/1000 = +0.2. This counts-to-expectation conversion is the bridge between sampler output and estimator-style quantities.',
    difficulty='hard',
)
