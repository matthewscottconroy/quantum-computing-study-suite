"""Problem: rep_dephasing_channel"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='rep_dephasing_channel',
    category='Repetition Code',
    difficulty='intermediate',
    question='The dephasing (phase-flip) channel with probability p has Kraus operators:',
    choices=[
        'K₀ = √(1-p) I and K₁ = √p Z',
        'K₀ = √(1-p) I and K₁ = √p X',
        'K₀ = √(1-p) I and K₁ = √p Y',
        'K₀ = I and K₁ = Z',
    ],
    correct_index=0,
    explanation='The dephasing channel applies Z (phase-flip) with probability p: K₀ = √(1-p) I and K₁ = √p Z. In the computational basis, ρ → (1-p)ρ + p ZρZ, which leaves diagonal elements (populations) unchanged while damping off-diagonal elements (coherences) by factor (1-2p). The 3-qubit phase-flip code protects against this channel.',
    hints=[
        'The dephasing channel kills off-diagonal coherences; which Pauli is responsible?',
    ],
    grade_mode=GradeMode.AUTO,
)
