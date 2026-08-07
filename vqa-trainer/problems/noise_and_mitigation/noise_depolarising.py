"""Problem: noise_depolarising"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='noise_depolarising',
    category='Noise & Mitigation',
    difficulty='beginner',
    question='What is a depolarising noise channel with error probability p?',
    choices=[
        'With probability p applies X, Y, or Z each with probability p/3, and with probability (1-p) does nothing: ρ → (1-p)ρ + (p/3)(XρX + YρY + ZρZ)',
        'With probability p flips the qubit (applies X only)',
        'Adds Gaussian noise to the rotation angle of every gate',
        'With probability p measures the qubit and resets it to |0⟩',
    ],
    correct_index=0,
    explanation='The single-qubit depolarising channel applies each of X, Y, Z with probability p/3 and leaves the state unchanged with probability 1-p. Equivalently: ρ → (1-p)ρ + (p/3)(XρX + YρY + ZρZ). The channel contracts the Bloch sphere by a factor (1-4p/3), mapping to the maximally mixed state I/2 when p=3/4. It is the most commonly used noise model in VQA analysis.',
    hints=[
        'Depolarising noise applies all three Pauli errors with equal probability.',
    ],
    grade_mode=GradeMode.MC,
)
