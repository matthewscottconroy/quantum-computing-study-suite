"""Question: qo_amplitude_prob"""
from core.models import Question

QUESTION = Question(
    id='qo_amplitude_prob',
    section='Quantum operations',
    question='A qubit is in the state 0.6|0⟩ + 0.8|1⟩. What is the probability of measuring 1?',
    options=[
        '0.64',
        '0.8',
        '0.36',
        '0.5',
    ],
    correct_index=0,
    explanation='Measurement probabilities are the squared magnitudes of amplitudes: P(1) = |0.8|² = 0.64. Reading the amplitude directly (0.8) or squaring the wrong amplitude (0.36 = P(0)) are the classic slips.',
    difficulty='easy',
)
