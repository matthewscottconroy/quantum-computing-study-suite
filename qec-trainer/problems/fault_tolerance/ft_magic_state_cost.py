"""Problem: ft_magic_state_cost"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ft_magic_state_cost',
    category='Fault Tolerance',
    difficulty='advanced',
    question='Approximately how many noisy T-gate applications are consumed per high-fidelity |T⟩ state in the standard 15-to-1 magic state distillation protocol?',
    choices=[
        '15 noisy |T⟩ states per one high-fidelity |T⟩ (15-to-1 protocol)',
        '7 noisy |T⟩ states (7-to-1 protocol using the Steane code)',
        '3 noisy |T⟩ states (repetition code distillation)',
        '100+ noisy states due to error correction overhead',
    ],
    correct_index=0,
    explanation='The 15-to-1 distillation protocol (Bravyi-Kitaev 2005): take 15 noisy copies of |T⟩ and use 15 Clifford operations and measurements to distill 1 high-fidelity copy. The output error rate scales as ε_out ≈ 35ε³ where ε is the input error rate, giving cubic improvement per round. Multiple rounds can reduce T-gate error below the threshold of the outer code. This is currently one of the dominant overheads in resource estimates for fault-tolerant quantum computers.',
    hints=[
        'The protocol uses the [[15,1,3]] Reed-Muller code for distillation.',
    ],
    grade_mode=GradeMode.AUTO,
)
