"""Problem: bp_qng_does_not_help"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='bp_qng_does_not_help',
    category='Barren Plateaus',
    difficulty='intermediate',
    question='Why does quantum natural gradient (QNG) not solve the barren plateau problem?',
    choices=[
        'The quantum Fisher information matrix (QFIM) also becomes exponentially ill-conditioned in the same parameter regions where gradients vanish',
        'QNG increases the circuit depth, making the barren plateau worse',
        'QNG uses gradient information, so if gradients are small, the QNG step is also small',
        'QNG is only applicable to circuits with commuting generators',
    ],
    correct_index=0,
    explanation='QNG updates θ ← θ - ηF⁻¹∇C. In a barren plateau, both ∇C ≈ 0 (exponentially small) AND the QFIM F becomes exponentially singular (ill-conditioned). The ratio F⁻¹∇C is thus 0/0 — the QFIM inversion amplifies the tiny gradient but also amplifies noise, giving no useful signal. Formally, for random circuits both the gradient and the QFIM concentrate around zero at the same exponential rate, so their ratio provides no useful directional information.',
    hints=[
        'The QFIM is not well-conditioned where gradients vanish — both are exponentially small.',
    ],
    grade_mode=GradeMode.MC,
)
