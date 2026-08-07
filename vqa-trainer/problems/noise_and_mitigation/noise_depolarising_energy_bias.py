"""Problem: noise_depolarising_energy_bias"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='noise_depolarising_energy_bias',
    category='Noise & Mitigation',
    difficulty='advanced',
    question='How does depolarising noise affect the VQE energy estimate — does it give an over-estimate or under-estimate of the true ground state energy?',
    choices=[
        'Over-estimate — depolarising noise mixes the state toward I/2ⁿ (the maximally mixed state), which has energy Tr(H)/2ⁿ ≥ E₀',
        'Under-estimate — noise introduces negative bias toward the ground state',
        'Unbiased — depolarising noise is symmetric and introduces no systematic shift in the energy',
        'Over-estimate or under-estimate depending on the circuit depth; shallow circuits under-estimate',
    ],
    correct_index=0,
    explanation='Depolarising noise drives ρ → (1-p)ρ + p·I/2ⁿ for each gate application. The energy becomes ⟨H⟩_noisy = (1-p)⟨H⟩_ideal + p·Tr(H)/2ⁿ. Since Tr(H)/2ⁿ = (E₀ + E₁ + ... + E_{2ⁿ-1})/2ⁿ is the average of all eigenvalues, and E₀ is the minimum, we have Tr(H)/2ⁿ ≥ E₀. Therefore ⟨H⟩_noisy ≥ (1-p)E₀ + p·E₀ = E₀ — the noisy energy is always above the true ground state energy. The noise-induced error is p·(Tr(H)/2ⁿ - E₀) ≥ 0. This upward bias is consistent with the variational principle.',
    hints=[
        'Depolarising noise moves the state toward I/2ⁿ — what is the energy of I/2ⁿ?',
    ],
    grade_mode=GradeMode.MC,
)
