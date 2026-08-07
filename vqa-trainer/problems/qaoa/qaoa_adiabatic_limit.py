"""Problem: qaoa_adiabatic_limit"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='qaoa_adiabatic_limit',
    category='QAOA',
    difficulty='intermediate',
    question='What is the QAOA adiabatic limit and what does it imply about approximation quality?',
    choices=[
        'As p→∞ with optimal parameters, QAOA reproduces the adiabatic algorithm and converges to the exact ground state of the cost Hamiltonian',
        'For very large p, QAOA parameters concentrate to fixed values independent of the problem instance',
        'The adiabatic limit means QAOA requires O(1/Δ²) layers where Δ is the spectral gap',
        'At large p, QAOA approximation ratio saturates at the classical Goemans-Williamson bound',
    ],
    correct_index=0,
    explanation='The continuous-time adiabatic algorithm slowly interpolates H(t) = (1-s(t))B + s(t)C from mixer B to cost C. QAOA with depth p can be viewed as a Trotterisation of this adiabatic path: as p→∞, the discrete steps become a continuous schedule and the adiabatic theorem guarantees convergence to the ground state if the schedule is slow enough. This formal connection proves QAOA is universal for combinatorial optimisation at infinite depth, motivating its use at finite p as an approximation.',
    hints=[
        'Think of QAOA as discretising a continuous adiabatic path.',
    ],
    grade_mode=GradeMode.MC,
)
