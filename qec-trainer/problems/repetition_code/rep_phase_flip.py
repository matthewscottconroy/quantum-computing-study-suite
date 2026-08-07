"""Problem: rep_phase_flip"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='rep_phase_flip',
    category='Repetition Code',
    difficulty='intermediate',
    question='The 3-qubit bit-flip code CANNOT correct which type of error?',
    choices=[
        'Phase-flip (Z) errors',
        'Bit-flip (X) errors',
        'Single qubit errors',
        'Identity (no-op)',
    ],
    correct_index=0,
    explanation='The bit-flip code uses Z-type stabilizers to detect X errors. It is completely blind to Z (phase-flip) errors — those commute with all stabilizers.',
    hints=[
        'Consider which errors commute with Z₁Z₂ and Z₂Z₃.',
    ],
    grade_mode=GradeMode.AUTO,
)
