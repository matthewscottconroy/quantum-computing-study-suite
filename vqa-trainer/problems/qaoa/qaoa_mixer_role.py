"""Problem: qaoa_mixer_role"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='qaoa_mixer_role',
    category='QAOA',
    difficulty='beginner',
    question='What is the role of the mixer unitary U_B(β) = e^{-iβB} in QAOA?',
    choices=[
        'Explores the solution space by inducing transitions between different bitstrings',
        'Encodes the cost function into phases of the quantum state',
        'Prepares the initial equal superposition state',
        'Measures the cost function expectation value',
    ],
    correct_index=0,
    explanation='The mixer B = Σᵢ Xᵢ (standard choice) drives transitions between computational basis states by rotating amplitudes. After U_C selectively phases high-cost states, U_B redistributes amplitudes, allowing low-cost states to constructively interfere. Together, repeated (U_C, U_B) layers implement a quantum walk that concentrates probability on high-quality solutions.',
    hints=[
        'One unitary encodes the problem; the other moves probability between solutions.',
    ],
    grade_mode=GradeMode.MC,
)
