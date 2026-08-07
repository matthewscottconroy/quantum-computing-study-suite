"""Problem: rep_concatenated_logical_rate"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='rep_concatenated_logical_rate',
    category='Repetition Code',
    difficulty='advanced',
    question='For a concatenated code with physical error rate p and threshold p_th, the logical error rate at level l is approximately:',
    choices=[
        'p_L ≈ p_th · (p/p_th)^(2^l)',
        'p_L ≈ p^l',
        'p_L ≈ (p/p_th)^l',
        'p_L ≈ p · 2^l',
    ],
    correct_index=0,
    explanation='For a concatenated [[n,1,d]] code with threshold p_th, the logical error rate at concatenation level l is p_L ≈ p_th · (p/p_th)^{2^l}. When p < p_th, p/p_th < 1 and this quantity decreases doubly-exponentially in l — each additional level squares the suppression factor. This is the key result of the threshold theorem for concatenated codes.',
    hints=[
        'Each level squares the ratio p/p_th in the exponent.',
    ],
    grade_mode=GradeMode.AUTO,
)
