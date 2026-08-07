"""Problem: surf_union_find"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='surf_union_find',
    category='Surface Code',
    difficulty='intermediate',
    question='The Union-Find decoder for the surface code achieves approximately what time complexity?',
    choices=[
        "Nearly linear O(n α(n)) where α is the inverse Ackermann function — much faster than MWPM's O(n³)",
        'O(n²) — quadratic but faster than MWPM',
        'O(n log n) — optimal for comparison-based algorithms',
        'O(n³) — same as MWPM but with smaller constant',
    ],
    correct_index=0,
    explanation="The Union-Find decoder (Delfosse & Nickerson 2021) achieves near-linear time O(n α(n)), where α is the extremely slow-growing inverse Ackermann function (essentially constant in practice). This is dramatically faster than MWPM's O(n³) blossom algorithm. The decoder 'grows' syndrome clusters using a union-find data structure and matches them when they collide. The trade-off: slightly suboptimal threshold compared to MWPM, but sufficient for practical fault-tolerant computation with fast real-time decoding.",
    hints=[
        'Union-Find is a data structure with nearly constant-time operations — the decoder inherits this.',
    ],
    grade_mode=GradeMode.AUTO,
)
