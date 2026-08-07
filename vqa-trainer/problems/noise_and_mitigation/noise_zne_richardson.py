"""Problem: noise_zne_richardson"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='noise_zne_richardson',
    category='Noise & Mitigation',
    difficulty='intermediate',
    question='For ZNE with Richardson extrapolation using noise factors λ₁=1 and λ₂=2, what is the zero-noise estimate E₀?',
    choices=[
        'E₀ = 2⟨O⟩(λ=1) − ⟨O⟩(λ=2)',
        'E₀ = [⟨O⟩(λ=1) + ⟨O⟩(λ=2)] / 2',
        'E₀ = ⟨O⟩(λ=1) − ⟨O⟩(λ=2)',
        'E₀ = ⟨O⟩(λ=1)² / ⟨O⟩(λ=2)',
    ],
    correct_index=0,
    explanation='Assuming linear noise model ⟨O⟩(λ) ≈ a + bλ, we have two equations: ⟨O⟩(1) = a + b and ⟨O⟩(2) = a + 2b. Solving for a (the zero-noise value at λ=0): b = ⟨O⟩(2) - ⟨O⟩(1), so a = ⟨O⟩(1) - b = ⟨O⟩(1) - (⟨O⟩(2) - ⟨O⟩(1)) = 2⟨O⟩(1) - ⟨O⟩(2). This is the order-1 Richardson extrapolation formula, exact if noise is linear in λ.',
    hints=[
        'Fit a line through two points and extrapolate to λ=0.',
    ],
    grade_mode=GradeMode.MC,
)
