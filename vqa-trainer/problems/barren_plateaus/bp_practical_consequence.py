"""Problem: bp_practical_consequence"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='bp_practical_consequence',
    category='Barren Plateaus',
    difficulty='beginner',
    question='What is the practical consequence of a barren plateau for gradient-based optimisation on a quantum device with finite shot budget?',
    choices=[
        'Exponentially many shots are needed to resolve the gradient signal, making optimisation infeasible',
        'The optimiser converges to the wrong local minimum instead of the global minimum',
        'The circuit parameters grow unbounded during training',
        'The quantum device overheats due to excessive gate operations',
    ],
    correct_index=0,
    explanation='In a barren plateau, Var[∂C/∂θ] ∝ 2^{-n}. To reliably estimate a gradient component at signal-to-noise ratio 1, you need shots ∝ 1/Var[∂C/∂θ] ∝ 2^n. For n=50 qubits this is ~10^15 shots — physically impossible. The gradient estimate is dominated by shot noise and the optimiser makes no progress, regardless of how sophisticated the classical optimiser is.',
    hints=[
        'The gradient is exponentially small — how many measurements do you need to detect it?',
    ],
    grade_mode=GradeMode.MC,
)
