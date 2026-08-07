"""Problem: qaoa_p_inf_limit"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='qaoa_p_inf_limit',
    category='QAOA',
    difficulty='intermediate',
    question='As p → ∞ with optimal parameters, QAOA is expected to:',
    choices=[
        'Converge to the exact maximum cut (or ground state of C)',
        'Require exponentially many parameters',
        'Fail due to barren plateaus',
        'Produce a uniform superposition',
    ],
    correct_index=0,
    explanation='For p → ∞, QAOA with optimal {γ, β} can approximate adiabatic quantum computation and converge to the exact ground state of C. In practice, p is kept small on NISQ hardware.',
    hints=[
        'Relate QAOA to the adiabatic algorithm in the large-p limit.',
    ],
    grade_mode=GradeMode.MC,
)
