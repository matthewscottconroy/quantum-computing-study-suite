"""Problem: ft_magic_state"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ft_magic_state',
    category='Fault Tolerance',
    difficulty='advanced',
    question='Why is magic state distillation needed for universal fault-tolerant computation?',
    choices=[
        'T gates are not transversal for most codes; magic states provide a fault-tolerant workaround',
        'Magic states eliminate the need for error correction',
        'T gates require two-qubit entanglement unavailable in codes',
        'Distillation reduces circuit depth exponentially',
    ],
    correct_index=0,
    explanation='By Eastin-Knill, no code has a transversal universal gate set. For most codes, T is not transversal. Magic state distillation: prepare many noisy |T⟩ = T|+⟩ states, then distill a high-fidelity one using Clifford operations only, then consume it via gate teleportation to implement T fault-tolerantly.',
    hints=[
        'Clifford + T is universal; Clifford is transversal; T requires another approach.',
    ],
    grade_mode=GradeMode.AUTO,
)
