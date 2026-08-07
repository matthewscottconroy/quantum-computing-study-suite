"""Problem: ps_spsa_stochastic"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ps_spsa_stochastic',
    category='Parameter Shift',
    difficulty='beginner',
    question="What is the 'stochastic' version of the parameter shift / gradient estimation used in SPSA, and what is its key efficiency?",
    choices=[
        'Perturbs all parameters simultaneously with a random ±1 vector, requiring only 2 circuit evaluations regardless of parameter count',
        'Randomly selects one parameter per step and applies the shift rule to only that parameter',
        'Uses random initialisation of parameters combined with the standard shift rule',
        'Applies random Pauli gates before each parameter shift to reduce shot noise',
    ],
    correct_index=0,
    explanation='SPSA simultaneously perturbs all p parameters by a random Bernoulli ±1 vector Δ: ∂C/∂θᵢ ≈ [C(θ+cΔ) - C(θ-cΔ)]/(2cΔᵢ). Only 2 circuit evaluations are needed for the entire gradient vector, versus 2p for the full parameter shift rule. The trade-off: each SPSA gradient estimate is noisy (high variance), requiring more optimisation iterations, but the per-step quantum cost is O(1) instead of O(p).',
    hints=[
        "The 'S' in SPSA stands for Simultaneous — all parameters shift at once.",
    ],
    grade_mode=GradeMode.MC,
)
