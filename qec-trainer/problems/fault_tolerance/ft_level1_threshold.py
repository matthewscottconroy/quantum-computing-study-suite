"""Problem: ft_level1_threshold"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ft_level1_threshold',
    category='Fault Tolerance',
    difficulty='beginner',
    question='If a code has fault-tolerance threshold p_th, what happens to the logical error rate when the physical rate p < p_th?',
    choices=[
        'The logical error rate is lower than p and decreases with increasing code distance',
        'The logical error rate equals p regardless of distance',
        'The logical error rate is higher than p due to syndrome measurement overhead',
        'The logical error rate is exactly zero',
    ],
    correct_index=0,
    explanation='Below threshold (p < p_th): each additional level of error correction or increase in code distance reduces the logical error rate. Specifically, for a distance-d code, the logical rate drops as ~(p/p_th)^{⌈d/2⌉}. This is the key operational guarantee: spending more resources on error correction always pays off when p < p_th.',
    hints=[
        "'Below threshold' means the code helps: more correction → lower logical error rate.",
    ],
    grade_mode=GradeMode.AUTO,
)
