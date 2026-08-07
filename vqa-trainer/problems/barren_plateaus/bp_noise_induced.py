"""Problem: bp_noise_induced"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='bp_noise_induced',
    category='Barren Plateaus',
    difficulty='advanced',
    question='Noise-induced barren plateaus (Wang et al. 2021) occur when:',
    choices=[
        'Depolarising noise makes the output state approach I/2ⁿ, flattening the landscape',
        'Shot noise exceeds the gradient signal',
        'The ansatz is not expressive enough',
        'The optimiser has too large a learning rate',
    ],
    correct_index=0,
    explanation='With a depolarising channel of rate p per layer, the state approaches the maximally mixed state I/2ⁿ exponentially fast in circuit depth. Since I/2ⁿ has no parameter dependence, gradients decay as (1-p)^d for depth d. This is unavoidable on noisy hardware without error correction.',
    hints=[
        'What does depolarising noise do to a quantum state in the infinite noise limit?',
    ],
    grade_mode=GradeMode.MC,
)
