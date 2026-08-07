"""Problem: steane_css"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='steane_css',
    category='Steane Code',
    difficulty='intermediate',
    question='The Steane code is a CSS code. What does CSS stand for?',
    choices=[
        'Calderbank-Shor-Steane',
        'Classical Stabilizer Syntax',
        'Coded Syndrome Scheme',
        'Clifford Subsystem Structure',
    ],
    correct_index=0,
    explanation='CSS = Calderbank-Shor-Steane (1996). CSS codes are built from two classical linear codes C₁ ⊇ C₂. They have separate X-type and Z-type stabilizers, making syndrome extraction simpler.',
    hints=[
        'Named after three authors who independently developed the construction.',
    ],
    grade_mode=GradeMode.AUTO,
)
