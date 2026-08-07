"""Problem: ansatz_adapt_vqe"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ansatz_adapt_vqe',
    category='Ansatz Design',
    difficulty='advanced',
    question='In ADAPT-VQE, how is the ansatz constructed?',
    choices=[
        'Operators are added one at a time from a pool, greedily selecting those with the largest gradient',
        'A fixed layer structure is repeated p times',
        'The ansatz is the full UCCSD expansion truncated at a fixed depth',
        'Parameters are randomly initialised and pruned based on variance',
    ],
    correct_index=0,
    explanation='ADAPT-VQE (Grimsley et al. 2019) builds the ansatz adaptively: at each step, compute |∂E/∂θ| for every operator in a pool (e.g. fermionic excitation operators), add the one with the largest gradient, then optimise all current parameters. Repeat until convergence. This gives compact, problem-adapted circuits with far fewer parameters than UCCSD.',
    hints=[
        'ADAPT = Adaptive Derivative-Assembled Pseudo-Trotter ansatz Variational Eigensolver.',
    ],
    grade_mode=GradeMode.MC,
)
