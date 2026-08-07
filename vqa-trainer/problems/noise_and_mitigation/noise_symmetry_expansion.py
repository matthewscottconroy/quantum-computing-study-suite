"""Problem: noise_symmetry_expansion"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='noise_symmetry_expansion',
    category='Noise & Mitigation',
    difficulty='advanced',
    question='How does symmetry expansion improve the VQE energy estimate without extra circuit depth?',
    choices=[
        'Applies symmetry operators {Sₖ} to expand the state ρ → (1/|G|)Σₖ Sₖ ρ Sₖ†, projecting to the physical symmetry sector and removing noise-induced leakage',
        'Expands the ansatz using symmetry operators as additional gates appended after the variational circuit',
        'Uses the symmetry group to reduce the number of Pauli terms measured, lowering shot noise',
        'Adds a symmetry-breaking penalty to the cost function that expands the convergence basin',
    ],
    correct_index=0,
    explanation='Symmetry expansion (McArdle et al. 2019) applies a symmetrisation operation to the noisy VQE output. If H commutes with a group G = {Sₖ}, the physical ground state is an eigenstate of each Sₖ. The symmetry-expanded state ρ_phys = (1/|G|)Σₖ Sₖρ Sₖ† has a lower or equal energy than ρ because it projects to the symmetric subspace. No extra quantum circuit depth is needed — the expansion is implemented classically by combining expectation values ⟨H·Sₖ⟩ measured on the existing circuit. This gives a tighter (lower) energy upper bound for the same circuit.',
    hints=[
        'Symmetry projection lowers the energy by forcing the state into the physical sector.',
    ],
    grade_mode=GradeMode.MC,
)
