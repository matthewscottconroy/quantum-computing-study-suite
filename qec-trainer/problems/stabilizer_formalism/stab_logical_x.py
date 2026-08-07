"""Problem: stab_logical_x"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='stab_logical_x',
    category='Stabilizer Formalism',
    difficulty='intermediate',
    question='A logical X operator L_X for a stabilizer code must satisfy:',
    choices=[
        'Commutes with all stabilizers but is not in the stabilizer group',
        'Anticommutes with all stabilizers',
        'Is the product of all stabilizer generators',
        'Has eigenvalue −1 on all code states',
    ],
    correct_index=0,
    explanation='L_X must commute with every stabilizer (to preserve the code space), but it must NOT be in the stabilizer group itself (otherwise it would act trivially). It anticommutes with the logical Z operator L_Z.',
    hints=[
        'Logical operators preserve the code space but distinguish |0̄⟩ from |1̄⟩.',
    ],
    grade_mode=GradeMode.AUTO,
)
