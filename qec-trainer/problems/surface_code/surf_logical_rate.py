"""Problem: surf_logical_rate"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='surf_logical_rate',
    category='Surface Code',
    difficulty='intermediate',
    question='For a distance-d surface code with physical error rate p < p_th, logical error rate scales as:',
    choices=[
        '∝ (p/p_th)^⌈d/2⌉',
        '∝ p^d',
        '∝ d · p',
        '∝ exp(-d)',
    ],
    correct_index=0,
    explanation='The logical error rate scales as (p/p_th)^⌈d/2⌉ below threshold. This exponential suppression in d is why the surface code is practical.',
    hints=[
        'Only weight ≥ ⌈d/2⌉ error chains can cause a logical error.',
    ],
    grade_mode=GradeMode.AUTO,
)
