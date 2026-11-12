"""Problem: qaoa_trotterised_annealing"""
from __future__ import annotations
from quantum_study.vqa_trainer.core.models import Problem, GradeMode

PROBLEM = Problem(
    id='qaoa_trotterised_annealing',
    category='QAOA',
    difficulty='advanced',
    question='How can QAOA be interpreted as Trotterised quantum annealing?',
    choices=[
        'QAOA layers are discrete time steps of adiabatic evolution from B to C; {βⱼ, γⱼ} set the schedule',
        'QAOA uses quantum annealing hardware (D-Wave) with a Trotterised digital gate sequence',
        'Trotterisation converts the QAOA cost unitary into a sum of local terms matching quantum annealing',
        'QAOA approximates finite-temperature quantum annealing using imaginary-time Trotterisation',
    ],
    correct_index=0,
    explanation="Quantum annealing evolves under H(s) = (1-s)B + sC from s=0 to s=1. A first-order Trotter discretisation of this with p steps gives e^{-iΔtH(s₁)}...e^{-iΔtH(sₚ)} ≈ e^{-iΔt(1-sⱼ)B}e^{-iΔtsⱼC} per step, matching the QAOA structure with βⱼ = Δt(1-sⱼ) and γⱼ = Δtsⱼ. This interpretation motivates the annealing-schedule initialisation for QAOA parameters and connects QAOA's performance to the spectral gap of H(s).",
    hints=[
        'Discretise the adiabatic time evolution using first-order Trotter and match to QAOA layers.',
    ],
    grade_mode=GradeMode.MC,
)
