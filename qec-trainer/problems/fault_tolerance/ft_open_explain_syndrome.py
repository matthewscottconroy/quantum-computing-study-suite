"""Problem: ft_open_explain_syndrome"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ft_open_explain_syndrome',
    category='Fault Tolerance',
    difficulty='intermediate',
    question='Explain in 3–5 sentences: why must syndrome measurements be repeated multiple times in fault-tolerant quantum error correction, rather than just once?',
    choices=[],
    correct_index=-1,
    explanation='Measurement itself is noisy. A single faulty measurement could trigger a wrong correction, introducing a new error. By repeating measurements d times (in a distance-d code), a measurement error appears as a temporal defect in the syndrome history, distinguishable from a physical qubit error — enabling the decoder to ignore it.',
    hints=[
        'What if the syndrome measurement itself introduces an error?',
    ],
    grade_mode=GradeMode.CLAUDE,
)
