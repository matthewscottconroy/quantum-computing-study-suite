"""Problem: rep_hamming_distance"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='rep_hamming_distance',
    category='Repetition Code',
    difficulty='intermediate',
    question='The Hamming distance between two classical codewords is defined as:',
    choices=[
        'The number of bit positions where they differ',
        'The number of bits they share in common',
        'The minimum number of errors needed to confuse them with a third codeword',
        'The absolute difference between their integer representations',
    ],
    correct_index=0,
    explanation='The Hamming distance d(c₁,c₂) counts the number of positions where codewords c₁ and c₂ differ. The minimum Hamming distance of a code (the minimum over all pairs of distinct codewords) determines its error correction capability. This concept carries over to quantum codes: the quantum code distance d is the minimum weight of a logical operator, analogous to the minimum Hamming distance between classical codewords.',
    hints=[
        'Count disagreements bit by bit — this is the classical precursor to quantum code distance.',
    ],
    grade_mode=GradeMode.AUTO,
)
