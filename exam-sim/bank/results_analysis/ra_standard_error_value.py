"""Question: ra_standard_error_value"""
from core.models import Question

QUESTION = Question(
    id='ra_standard_error_value',
    section='Results analysis',
    question="A single-qubit circuit is sampled 10 000 times and outcome '0' occurs 5000 times. What is the approximate standard error of the estimated probability p̂ = 0.5?",
    options=[
        '0.005 — √(p̂(1 − p̂)/N) = √(0.25/10000)',
        '0.05 — √(p̂(1 − p̂)/N) = √(0.25/100)',
        '0.25 — the variance p̂(1 − p̂) is itself the standard error',
        '0.0 — the observed split is exactly 50/50, so there is no uncertainty',
    ],
    correct_index=0,
    explanation='For a binomial frequency the standard error is √(p̂(1 − p̂)/N) = √(0.25/10000) = 0.005, i.e. about ±0.5 % on a 50/50 split at 10 000 shots. p̂(1 − p̂) = 0.25 is the per-shot VARIANCE, not the error on the mean, and an exactly balanced sample is still a sample — matching the expected value says nothing about the width of the sampling distribution.',
    difficulty='hard',
)
