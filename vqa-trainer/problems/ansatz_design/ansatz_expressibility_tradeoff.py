"""Problem: ansatz_expressibility_tradeoff"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ansatz_expressibility_tradeoff',
    category='Ansatz Design',
    difficulty='advanced',
    question='Describe the expressibility–trainability tradeoff in VQA ansatz design.',
    choices=[
        'Higher expressibility (larger reachable state space) increases barren plateau risk and makes training harder',
        'More expressive ansätze always have more parameters, increasing training cost linearly',
        'Trainability and expressibility are independent properties that do not interact',
        'The tradeoff only applies to hardware-efficient ansätze, not chemically motivated ones',
    ],
    correct_index=0,
    explanation='Expressibility measures how well the ansatz explores the full unitary group U(2ⁿ). Highly expressive ansätze approach random unitaries (approximate 2-designs), causing the gradient variance to decay as 2^{-n} — a barren plateau. Less expressive, problem-motivated ansätze (e.g. UCCSD, symmetry-preserving) have smaller search spaces with larger gradients, but may not represent the ground state if the true state lies outside their span. Optimal ansatz design navigates this tradeoff: expressive enough to capture the solution, structured enough to avoid barren plateaus.',
    hints=[
        'Can an ansatz be both maximally expressive AND easy to train? Why or why not?',
    ],
    grade_mode=GradeMode.MC,
)
