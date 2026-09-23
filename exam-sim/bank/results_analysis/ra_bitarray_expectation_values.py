"""Question: ra_bitarray_expectation_values"""
from core.models import Question

QUESTION = Question(
    id='ra_bitarray_expectation_values',
    section='Results analysis',
    question='A 2-qubit run gives `{\'00\': 450, \'01\': 60, \'10\': 90, \'11\': 400}` over 1000 shots. What does `ba.expectation_values("ZZ")` return?',
    options=[
        '0.7 — the shot-averaged parity (+1 for even-weight keys, −1 for odd)',
        "0.45 — the probability of the most likely outcome '00'",
        "0.85 — the total probability of '00' and '11'",
        'It raises — BitArray holds raw bits, so expectation values need an Estimator',
    ],
    correct_index=0,
    explanation="BitArray.expectation_values(observables) evaluates diagonal (Z/I-only) observables directly from sampled bits: each shot contributes the product of ±1 eigenvalues, which for ZZ is +1 on '00'/'11' and −1 on '01'/'10', giving (450 + 400 − 60 − 90)/1000 = 0.7. Note the intuitive-looking 0.85 is P(even), and ⟨ZZ⟩ = 2·P(even) − 1. Non-diagonal observables still require basis rotation or an Estimator.",
    difficulty='hard',
)
