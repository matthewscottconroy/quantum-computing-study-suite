"""Problem: ft_pseudothreshold"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ft_pseudothreshold',
    category='Fault Tolerance',
    difficulty='intermediate',
    question='The level-1 pseudothreshold p̃ of a fault-tolerant code is defined as the physical error rate below which a single level of encoding reduces the logical error rate. For a code with threshold p_th, p̃ is typically:',
    choices=[
        'Higher than the true threshold p_th — the pseudothreshold is optimistic because it only considers single-level encoding overhead',
        'Equal to the true threshold p_th by definition',
        'Lower than p_th — encoding always hurts at level 1',
        'Independent of the code — always 1%',
    ],
    correct_index=0,
    explanation='The pseudothreshold is defined as p̃ such that p_L(p̃) = p̃ — the break-even point where encoding helps. For a level-1 code, p_L ≈ C·p² where C counts the number of ways to get two faults. The pseudothreshold is p̃ = 1/C, which can be much higher than the true threshold (e.g., 1% vs 0.1%). The true threshold, obtained by analyzing multiple levels of concatenation, is typically lower because higher-level encoding introduces more overhead per level, requiring a more stringent break-even.',
    hints=[
        'Pseudothreshold: level-1 encoding breaks even. True threshold: all levels benefit.',
    ],
    grade_mode=GradeMode.AUTO,
)
