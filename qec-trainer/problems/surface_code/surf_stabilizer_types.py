"""Problem: surf_stabilizer_types"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='surf_stabilizer_types',
    category='Surface Code',
    difficulty='beginner',
    question='The surface code uses two types of stabilizers. What are they?',
    choices=[
        'X-type plaquette stabilizers (XXXX) and Z-type vertex stabilizers (ZZZZ)',
        'ZZ stabilizers and XX stabilizers in a 1D chain',
        'Only Z stabilizers (it is a CSS code with one type)',
        'YY and XX stabilizers on alternating rows',
    ],
    correct_index=0,
    explanation='The surface code has X-type stabilizers (products of X on 4 data qubits around a face) and Z-type stabilizers (products of Z on 4 data qubits around a vertex). X errors (bit flips) trigger Z stabilizers; Z errors (phase flips) trigger X stabilizers.',
    hints=[
        'One type detects X errors; the other detects Z errors.',
    ],
    grade_mode=GradeMode.AUTO,
)
