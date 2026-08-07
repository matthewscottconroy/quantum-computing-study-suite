"""Problem: stab_def"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='stab_def',
    category='Stabilizer Formalism',
    difficulty='beginner',
    question='A stabilizer S of a state |ψ⟩ satisfies S|ψ⟩ = ?',
    choices=[
        '+|ψ⟩',
        '−|ψ⟩',
        '0',
        'iS|ψ⟩',
    ],
    correct_index=0,
    explanation='By definition, a stabilizer S satisfies S|ψ⟩ = +1·|ψ⟩. The state is a +1 eigenstate.',
    hints=[
        'Stabilizers are operators that leave the state unchanged.',
    ],
    grade_mode=GradeMode.AUTO,
)
