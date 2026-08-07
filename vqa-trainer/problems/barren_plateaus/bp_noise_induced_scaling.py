"""Problem: bp_noise_induced_scaling"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='bp_noise_induced_scaling',
    category='Barren Plateaus',
    difficulty='advanced',
    question='How does the noise-induced barren plateau scale with circuit depth d and qubit count n for a depolarising channel with per-layer error rate p?',
    choices=[
        'Gradient decays as (1-p)^d with depth d — exponential in depth, not qubit count; unlike shot-noise BPs which scale with n',
        'Gradient decays as (1-p)^n — exponential in qubit count only, independent of depth',
        'Gradient decays as (1-p)^{nd} — exponential in both depth and qubit count simultaneously',
        'Gradient decays polynomially as 1/(pd) for small error rates',
    ],
    correct_index=0,
    explanation="Wang et al. (2021) showed that with a depolarising channel applied each circuit layer, the output state approaches I/2ⁿ with rate (1-p)^d per layer. The gradient of any observable ⟨O⟩ scales as (1-p)^d since deeper circuits have more noise-induced erasure of the parameter dependence. This is exponential in depth d but does not directly depend on n — unlike McClean et al.'s barren plateau which is exponential in n (for random circuits at fixed depth). The two phenomena can compound: noise-induced BP is exponential in depth, random-circuit BP is exponential in qubit count.",
    hints=[
        'Depolarising noise per layer acts as (1-p) factor — multiply over d layers.',
    ],
    grade_mode=GradeMode.MC,
)
