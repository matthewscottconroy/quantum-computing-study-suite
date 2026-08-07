"""Problem: vqe_variational_principle"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='vqe_variational_principle',
    category='VQE Fundamentals',
    difficulty='beginner',
    question='The VQE variational principle states that for any trial state |ψ(θ)⟩ and Hamiltonian H with ground energy E₀, which inequality always holds?',
    choices=[
        '⟨ψ(θ)|H|ψ(θ)⟩ ≥ E₀',
        '⟨ψ(θ)|H|ψ(θ)⟩ ≤ E₀',
        '⟨ψ(θ)|H|ψ(θ)⟩ = E₀  for all θ',
        '⟨ψ(θ)|H|ψ(θ)⟩ ≥ 0  always',
    ],
    correct_index=0,
    explanation='The variational principle: ⟨ψ(θ)|H|ψ(θ)⟩ ≥ E₀ for any normalised |ψ(θ)⟩. Equality holds iff |ψ(θ)⟩ is the ground state. Minimising over θ gives an upper bound on E₀.',
    hints=[
        'The trial state energy is always at least the ground state energy.',
    ],
    grade_mode=GradeMode.MC,
)
