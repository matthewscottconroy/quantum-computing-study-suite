"""Problem: vqe_excited_state_penalty"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='vqe_excited_state_penalty',
    category='VQE Fundamentals',
    difficulty='intermediate',
    question='How does the orthogonally constrained VQE (or penalty-based excited-state VQE) find excited states?',
    choices=[
        'Adds an overlap penalty β|⟨ψ₀|ψ(θ)⟩|² to the cost function, pushing optimisation away from the ground state toward the first excited state',
        'Applies quantum phase estimation to identify excited-state energies from the ground-state circuit',
        'Replaces the Hamiltonian H with H² so that all eigenstates become ground states of H²',
        'Uses the variational principle for excited states, which states that ⟨ψ|H|ψ⟩ ≤ E₁ for any |ψ⟩ orthogonal to |ψ₀⟩',
    ],
    correct_index=0,
    explanation='The penalty-based approach minimises C(θ) = ⟨ψ(θ)|H|ψ(θ)⟩ + β|⟨ψ₀(θ*)|ψ(θ)⟩|², where |ψ₀(θ*)⟩ is the previously converged ground state and β > 0 is a penalty weight. The penalty term adds energy to states that overlap with the ground state, forcing the optimiser to find the first excited state. Iterating this procedure gives successive excited states. The method requires storing previously found states and evaluating overlap circuits, which adds quantum circuit overhead.',
    hints=[
        'You penalise the cost function to avoid the already-found lower eigenstates.',
    ],
    grade_mode=GradeMode.MC,
)
