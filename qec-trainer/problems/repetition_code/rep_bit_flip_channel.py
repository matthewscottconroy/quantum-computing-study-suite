"""Problem: rep_bit_flip_channel"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='rep_bit_flip_channel',
    category='Repetition Code',
    difficulty='intermediate',
    question='The bit-flip channel with probability p has Kraus operators:',
    choices=[
        'K₀ = √(1-p) I and K₁ = √p X',
        'K₀ = √(1-p) I and K₁ = √p Z',
        'K₀ = (1-p) I and K₁ = p X',
        'K₀ = √p X and K₁ = √(1-p) Z',
    ],
    correct_index=0,
    explanation='The bit-flip channel applies X (flips the qubit) with probability p and leaves it unchanged with probability 1-p. Its Kraus representation is: K₀ = √(1-p) I (no flip) and K₁ = √p X (flip). The density matrix evolves as ρ → K₀ρK₀† + K₁ρK₁† = (1-p)ρ + p XρX. This is the simplest quantum channel and the target of the repetition code.',
    hints=[
        'A Kraus operator K_i has weight √(probability of that outcome).',
    ],
    grade_mode=GradeMode.AUTO,
)
