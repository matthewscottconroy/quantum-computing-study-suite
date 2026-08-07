"""Problem: stab_one_stabilizer"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='stab_one_stabilizer',
    category='Stabilizer Formalism',
    difficulty='beginner',
    question='Which single-qubit Pauli operator stabilizes |1⟩?',
    choices=[
        '−Z',
        '+Z',
        '+X',
        '−X',
    ],
    correct_index=0,
    explanation='Z|1⟩ = −|1⟩, so −Z stabilizes |1⟩ (it is a −1 eigenstate of Z). This is why |0⟩ and |1⟩ are distinguished by the sign of their Z stabilizer.',
    hints=[
        'Z|1⟩ = −|1⟩, so which operator has +1 eigenvalue on |1⟩?',
    ],
    grade_mode=GradeMode.AUTO,
)
