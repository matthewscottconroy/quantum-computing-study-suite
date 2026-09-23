"""Question: ra_parity_single_qubit"""
from core.models import Question

QUESTION = Question(
    id='ra_parity_single_qubit',
    section='Results analysis',
    question="Using the same 1000-shot result `{'00': 400, '01': 150, '10': 50, '11': 400}`, what are ⟨Z on qubit 0⟩ and ⟨Z on qubit 1⟩?",
    options=[
        '−0.1 and +0.1 — qubit 0 is the RIGHTMOST character of each key, qubit 1 the leftmost',
        '+0.1 and −0.1 — qubit 0 is the leftmost character of each key',
        '0.6 and 0.6 — a single-qubit Z expectation is read from the full-string parity',
        '−0.1 and −0.1 — both single-qubit marginals must agree in a correlated state',
    ],
    correct_index=0,
    explanation='Marginalize first, then take the parity. Qubit 0 is the rightmost character: P(0) = (400 + 50)/1000 = 0.45 and P(1) = 0.55, so ⟨IZ⟩ = 0.45 − 0.55 = −0.1. Qubit 1 is the leftmost: P(0) = (400 + 150)/1000 = 0.55, giving ⟨ZI⟩ = +0.1. Reading the string big-endian swaps the two signs — the single most common endianness error in results analysis.',
    difficulty='hard',
)
