"""Problem: ps_rule_formula"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ps_rule_formula',
    category='Parameter Shift',
    difficulty='beginner',
    question='For a gate G(θ) = e^{-iθP/2} with P a Pauli (eigenvalues ±1), the parameter shift rule gives ∂⟨H⟩/∂θ = ?',
    choices=[
        '[⟨H⟩(θ+π/2) - ⟨H⟩(θ-π/2)] / 2',
        '[⟨H⟩(θ+ε) - ⟨H⟩(θ-ε)] / (2ε)',
        '[⟨H⟩(θ+π) - ⟨H⟩(θ)] / π',
        '⟨∂G/∂θ · H + H · ∂G†/∂θ⟩',
    ],
    correct_index=0,
    explanation='The parameter shift rule: ∂⟨H⟩/∂θ = [⟨H⟩(θ+π/2) - ⟨H⟩(θ-π/2)] / 2. This is exact (not an approximation like finite difference) and requires exactly 2 circuit evaluations per parameter — hence 2p evaluations for a p-parameter circuit.',
    hints=[
        'The shift is π/2, not a small ε.',
    ],
    grade_mode=GradeMode.MC,
)
