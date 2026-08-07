"""Problem: ft_pieceable"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ft_pieceable',
    category='Fault Tolerance',
    difficulty='advanced',
    question='What is pieceable fault tolerance?',
    choices=[
        'A method where a non-transversal gate is broken into pieces, with error correction applied between pieces to prevent fault propagation',
        'Applying multiple small fault-tolerant gates in parallel to implement one large gate',
        'A technique that pieces together different codes to cover different error types',
        'Dividing the code block into sub-blocks each protected by a simpler code',
    ],
    correct_index=0,
    explanation="Pieceable fault tolerance (Yoder, Takagi, Chuang 2016): some gates are not transversal but can be decomposed into a sequence of partial operations, each of which preserves fault-tolerance when followed by error correction. Each 'piece' creates at most one correctable error; intermediate correction resets the error count. This allows non-transversal gates (like T for some codes, or CCZ) to be applied fault-tolerantly without full magic state distillation, at the cost of more error correction rounds.",
    hints=[
        'Piecing a gate: apply part of it, correct errors, apply the rest — each piece is safe.',
    ],
    grade_mode=GradeMode.AUTO,
)
