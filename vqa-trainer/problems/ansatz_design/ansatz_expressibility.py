"""Problem: ansatz_expressibility"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ansatz_expressibility',
    category='Ansatz Design',
    difficulty='intermediate',
    question='Expressibility of a parameterised ansatz is measured by how well it can approximate:',
    choices=[
        'The full unitary group U(2ⁿ) — i.e. any n-qubit state',
        'The Clifford group only',
        'A specific target state',
        'All product states',
    ],
    correct_index=0,
    explanation='Expressibility quantifies how uniformly the ansatz samples from the Hilbert space. A highly expressible ansatz can reach states close to any unitary, but expressible ≠ trainable — highly expressible circuits often suffer barren plateaus.',
    hints=[
        'More expressible means closer to a unitary 2-design.',
    ],
    grade_mode=GradeMode.MC,
)
