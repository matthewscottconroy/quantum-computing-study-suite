"""Question: ra_parity_zz"""
from core.models import Question

QUESTION = Question(
    id='ra_parity_zz',
    section='Results analysis',
    question="A 2-qubit circuit gives `{'00': 400, '01': 150, '10': 50, '11': 400}` over 1000 shots. What is the estimate of ⟨Z⊗Z⟩?",
    options=[
        '0.6 — (400 + 400 − 150 − 50) / 1000, using +1 for even-parity keys and −1 for odd',
        "0.8 — the combined probability of the correlated outcomes '00' and '11'",
        '0.35 — (400 − 150 − 50 + 400) / 2000, averaging over both qubits',
        '1.0 — ZZ has eigenvalues ±1, so its average over any sample is ±1',
    ],
    correct_index=0,
    explanation="⟨ZZ⟩ is the average of the parity eigenvalue: keys with an EVEN number of 1s ('00', '11') contribute +1 and odd-parity keys ('01', '10') contribute −1, giving (800 − 200)/1000 = 0.6. The tempting 0.8 is P(even); the relation is ⟨ZZ⟩ = 2·P(even) − 1. No basis change is needed because ZZ is diagonal in the computational basis.",
    difficulty='hard',
)
