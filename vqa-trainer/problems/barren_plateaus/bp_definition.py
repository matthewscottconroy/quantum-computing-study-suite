"""Problem: bp_definition"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='bp_definition',
    category='Barren Plateaus',
    difficulty='beginner',
    question='A barren plateau in a VQA landscape is characterised by:',
    choices=[
        'Gradients exponentially small in the number of qubits',
        'Many local minima of equal energy',
        'The cost function being constant',
        'Circuit depth exceeding qubit count',
    ],
    correct_index=0,
    explanation='In a barren plateau, Var[∂C/∂θ] ∝ 2^{-n}. Gradients vanish exponentially, making gradient-based optimisation impractical since exponentially many shots are needed to resolve the signal.',
    hints=[
        'The problem is with gradient magnitude, not the cost value itself.',
    ],
    grade_mode=GradeMode.MC,
)
