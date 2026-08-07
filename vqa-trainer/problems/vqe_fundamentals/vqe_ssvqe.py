"""Problem: vqe_ssvqe"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='vqe_ssvqe',
    category='VQE Fundamentals',
    difficulty='intermediate',
    question='The SSVQE (Subspace-Search VQE) algorithm targets excited states. How does it work?',
    choices=[
        'Minimises a weighted sum of energies for a set of orthogonal ansatz states to find multiple eigenstates',
        'Adds a penalty term for the ground state to push the optimisation to higher energies',
        'Uses the variational principle applied to the square of the Hamiltonian',
        'Performs VQE then applies a quantum phase kick to access excited states',
    ],
    correct_index=0,
    explanation='SSVQE prepares k orthogonal trial states |ψ₁(θ)⟩,...,|ψₖ(θ)⟩ and minimises the weighted cost C = Σᵢ wᵢ⟨ψᵢ(θ)|H|ψᵢ(θ)⟩ with w₁ > w₂ > ... > wₖ > 0. The ordering of weights forces the optimiser to find distinct energy eigenstates. This allows simultaneous access to the ground state and several excited states without the folded-spectrum trick that requires squaring the Hamiltonian.',
    hints=[
        'SSVQE = Subspace-Search VQE; it uses multiple orthogonal states simultaneously.',
    ],
    grade_mode=GradeMode.MC,
)
