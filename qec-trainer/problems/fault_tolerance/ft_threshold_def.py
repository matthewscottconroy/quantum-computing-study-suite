"""Problem: ft_threshold_def"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ft_threshold_def',
    category='Fault Tolerance',
    difficulty='beginner',
    question='What does the threshold theorem guarantee?',
    choices=[
        'If physical error rate < threshold, arbitrarily long computations are possible with poly overhead',
        'Physical error rate can be made exactly zero',
        'All errors become detectable at the threshold',
        'Clifford gates become universal below the threshold',
    ],
    correct_index=0,
    explanation='The threshold theorem: if p < p_th, fault-tolerant quantum computation can be performed for any circuit depth with only O(polylog) overhead in resources.',
    hints=[
        "'Threshold' is a phase transition: below it, more error correction helps.",
    ],
    grade_mode=GradeMode.AUTO,
)
