"""Problem: noise_richardson_order3"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='noise_richardson_order3',
    category='Noise & Mitigation',
    difficulty='intermediate',
    question='For ZNE with Richardson extrapolation using noise factors λ=1, λ=2, λ=3, what is the formula for the zero-noise estimate E₀ (order-2 Richardson extrapolation)?',
    choices=[
        'E₀ = (3/2)⟨O⟩(1) - 2⟨O⟩(2) + (1/2)⟨O⟩(3)',
        'E₀ = 3⟨O⟩(1) - 3⟨O⟩(2) + ⟨O⟩(3)',
        'E₀ = [⟨O⟩(1) + ⟨O⟩(3)] / 2 − ⟨O⟩(2)',
        'E₀ = (6⟨O⟩(1) - 3⟨O⟩(2) + ⟨O⟩(3)) / 4',
    ],
    correct_index=0,
    explanation='Assuming ⟨O⟩(λ) ≈ a + bλ + cλ² (quadratic noise model), we solve the 3×3 system: ⟨O⟩(1)=a+b+c, ⟨O⟩(2)=a+2b+4c, ⟨O⟩(3)=a+3b+9c. Solving for a = E₀: from the Lagrange interpolation at λ=0, a = (3/2)⟨O⟩(1) - 2⟨O⟩(2) + (1/2)⟨O⟩(3). This cancels the linear and quadratic noise terms, leaving the exact E₀ if the noise is truly quadratic in λ. Verify: plug in ⟨O⟩(λ)=a to confirm a is recovered.',
    hints=[
        'Fit a quadratic through 3 points and evaluate at λ=0 — use Lagrange interpolation.',
    ],
    grade_mode=GradeMode.MC,
)
