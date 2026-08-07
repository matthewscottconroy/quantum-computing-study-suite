"""Problem: stab_zero_stabilizer"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='stab_zero_stabilizer',
    category='Stabilizer Formalism',
    difficulty='beginner',
    question='Which single-qubit Pauli operator stabilizes |0⟩?',
    choices=[
        '+Z',
        '−Z',
        '+X',
        '+Y',
    ],
    correct_index=0,
    explanation='Z|0⟩ = +1·|0⟩, so +Z stabilizes |0⟩. Correspondingly, −Z stabilizes |1⟩ because Z|1⟩ = −|1⟩.',
    hints=[
        'Apply Z to |0⟩ and check the eigenvalue.',
    ],
    grade_mode=GradeMode.AUTO,
)
