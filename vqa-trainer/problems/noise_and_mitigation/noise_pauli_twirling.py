"""Problem: noise_pauli_twirling"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='noise_pauli_twirling',
    category='Noise & Mitigation',
    difficulty='intermediate',
    question='Pauli twirling converts an arbitrary noise channel into:',
    choices=[
        'A Pauli channel (stochastic mixture of Pauli errors)',
        'A depolarising channel with strength 0',
        'A unitary rotation',
        'A purely dephasing (Z-only) channel',
    ],
    correct_index=0,
    explanation='Pauli twirling: conjugate each gate with a random Pauli P before and P† after. Averaging over P ∈ {I,X,Y,Z}^n converts any noise channel E into a Pauli channel Σ_P p_P P(·)P† with the same eigenvalues of the Choi matrix diagonal. Pauli channels are easier to characterise, simulate, and mitigate.',
    hints=[
        'Twirling symmetrises the noise channel over the Pauli group.',
    ],
    grade_mode=GradeMode.MC,
)
