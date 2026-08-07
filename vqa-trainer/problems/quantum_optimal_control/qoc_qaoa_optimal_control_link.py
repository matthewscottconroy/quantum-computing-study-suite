"""Problem: qoc_qaoa_optimal_control_link"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='qoc_qaoa_optimal_control_link',
    category='Optimal Control',
    difficulty='advanced',
    question='What is the relationship between QAOA and digitised adiabatic quantum computing / optimal control?',
    choices=[
        'QAOA with optimal {γ,β} parameters is equivalent to a Trotterised adiabatic schedule; optimal control theory can be used to find QAOA parameters that minimise circuit depth for a target approximation ratio',
        'QAOA and adiabatic quantum computing are completely different paradigms with no formal connection',
        'QAOA can be directly executed on D-Wave hardware by converting γ and β to annealing schedule parameters',
        'Optimal control improves QAOA by replacing the digital cost unitary with a continuous-time evolution',
    ],
    correct_index=0,
    explanation="QAOA with p layers implements a digitised version of adiabatic quantum computation: the {γⱼ,βⱼ} parameters encode a discrete annealing schedule H(t) interpolating from mixer B to cost C. Optimal control theory asks: what is the best p-step schedule to maximise the overlap with the ground state? This connects QAOA parameter optimisation to the optimal control problem of finding the fastest adiabatic path (quantum speed limit for annealing). Results from QOC suggest that QAOA schedules matching 'bang-bang' optimal control (alternating fast and slow evolution) can outperform smooth annealing schedules at the same circuit depth.",
    hints=[
        'QAOA layers are discrete steps of an annealing schedule — optimal control sets the step sizes.',
    ],
    grade_mode=GradeMode.MC,
)
