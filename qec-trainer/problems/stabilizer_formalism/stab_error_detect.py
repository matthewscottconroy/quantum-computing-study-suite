"""Problem: stab_error_detect"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='stab_error_detect',
    category='Stabilizer Formalism',
    difficulty='advanced',
    question='An error E is detectable by a stabilizer code iff:',
    choices=[
        'E anticommutes with at least one stabilizer generator',
        'E commutes with all stabilizer generators',
        'E is a Pauli X operator',
        'E has weight greater than d/2',
    ],
    correct_index=0,
    explanation='If error E anticommutes with stabilizer Sᵢ, measuring Sᵢ yields −1 (the syndrome flags the error). If E commutes with all stabilizers, it is either in the stabilizer group (trivial) or a logical operator (undetectable).',
    hints=[
        'Syndrome measurement detects anticommutation with stabilizers.',
    ],
    grade_mode=GradeMode.AUTO,
)
