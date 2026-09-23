"""Question: ra_expectation_std_error"""
from core.models import Question

QUESTION = Question(
    id='ra_expectation_std_error',
    section='Results analysis',
    question='A Z-basis measurement of 1000 shots yields ⟨Z⟩ = 0.6. What is the approximate standard error on that expectation value?',
    options=[
        '0.025 — √((1 − ⟨Z⟩²)/N) = √(0.64/1000)',
        '0.0155 — √(⟨Z⟩(1 − ⟨Z⟩)/N), the formula for a probability',
        '0.6 — the expectation value is its own uncertainty scale',
        '0.0008 — the variance 0.64 divided by N',
    ],
    correct_index=0,
    explanation='Each shot returns ±1, so the per-shot variance is ⟨Z²⟩ − ⟨Z⟩² = 1 − 0.36 = 0.64 (using Z² = I), and the error on the mean is √(0.64/1000) ≈ 0.0253. The binomial formula √(p(1−p)/N) applies to a PROBABILITY, not to a ±1-valued observable — the two differ by the factor of 2 between p and ⟨Z⟩ = 2p − 1. Note the error is largest at ⟨Z⟩ = 0 and vanishes as ⟨Z⟩ → ±1.',
    difficulty='hard',
)
