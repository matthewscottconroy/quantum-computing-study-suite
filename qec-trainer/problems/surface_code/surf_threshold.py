"""Problem: surf_threshold"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='surf_threshold',
    category='Surface Code',
    difficulty='beginner',
    question='The approximate fault-tolerance threshold for the surface code is:',
    choices=[
        '~1%',
        '~0.01%',
        '~10%',
        '~50%',
    ],
    correct_index=0,
    explanation='The surface code threshold is approximately 1% physical error rate. Below this threshold, increasing the code distance d reduces the logical error rate exponentially.',
    hints=[
        "It's the highest threshold of any known topological code.",
    ],
    grade_mode=GradeMode.AUTO,
)
