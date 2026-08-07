"""Problem: pec_definition"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='pec_definition',
    category='Noise & Mitigation',
    difficulty='intermediate',
    question='Probabilistic Error Cancellation (PEC) achieves error mitigation by:',
    choices=[
        'Representing ideal gates as quasi-probability distributions over noisy operations',
        'Repeating circuits and averaging out stochastic noise',
        'Applying Clifford twirling to convert noise to depolarising',
        'Using ancilla qubits to detect and correct errors',
    ],
    correct_index=0,
    explanation='PEC decomposes ideal gate ε_ideal as Σᵢ cᵢ εᵢ (quasi-probability: cᵢ can be negative). Sample from |cᵢ| distribution, apply εᵢ with sign(cᵢ). The overhead is γ² where γ = Σᵢ|cᵢ| ≥ 1 — grows exponentially with circuit depth.',
    hints=[
        'It uses quasi-probability decompositions — some weights are negative.',
    ],
    grade_mode=GradeMode.MC,
)
