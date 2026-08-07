"""Problem: ansatz_unitary_2design"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ansatz_unitary_2design',
    category='Ansatz Design',
    difficulty='intermediate',
    question='What is a unitary 2-design, and why is it relevant to barren plateaus in ansatz design?',
    choices=[
        'An ensemble of unitaries that matches the Haar measure up to 2nd moments; random ansätze forming 2-designs exhibit barren plateaus',
        'A circuit with exactly 2 layers of entangling gates',
        'An ansatz whose output states form a 2-dimensional subspace of Hilbert space',
        'A design pattern where each parameter appears exactly twice in the circuit',
    ],
    correct_index=0,
    explanation='A unitary 2-design reproduces the first two moments of the Haar (uniform) measure over the unitary group. The Clifford group is a 3-design and a fortiori a 2-design. If a parameterised ansatz forms an approximate 2-design, then for global cost functions Var[∂C/∂θ] ∝ 2^{-n} (barren plateau), because the gradients average to zero over the uniform distribution. This provides the theoretical basis for the McClean et al. (2018) barren plateau result: sufficiently deep random ansätze form approximate 2-designs.',
    hints=[
        "A 2-design is 'like sampling uniformly from all unitaries' — think about what random means for gradients.",
    ],
    grade_mode=GradeMode.MC,
)
