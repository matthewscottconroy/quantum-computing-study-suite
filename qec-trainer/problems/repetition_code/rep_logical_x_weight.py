"""Problem: rep_logical_x_weight"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='rep_logical_x_weight',
    category='Repetition Code',
    difficulty='intermediate',
    question='In the 3-qubit bit-flip code, what is the weight of the logical X̄ operator?',
    choices=[
        'Weight 3 (must flip all 3 qubits)',
        'Weight 1 (flip any single qubit)',
        'Weight 2 (flip any two qubits)',
        'Weight 0 (identity)',
    ],
    correct_index=0,
    explanation='The logical X̄ operator must map |0̄⟩ = |000⟩ to |1̄⟩ = |111⟩ and vice versa. The minimum weight operator achieving this is X₁X₂X₃ (weight 3), which flips all three qubits simultaneously. Weight-1 or weight-2 X operators only take the state outside the codespace.',
    hints=[
        'Logical X̄ must swap |000⟩ ↔ |111⟩. What is the minimum number of bit-flips needed?',
    ],
    grade_mode=GradeMode.AUTO,
)
