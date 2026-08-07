"""Problem: steane_syndrome_bits"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='steane_syndrome_bits',
    category='Steane Code',
    difficulty='intermediate',
    question='When a single X error occurs on qubit 3 of the Steane code, how many syndrome bits are produced and what do they indicate?',
    choices=[
        '3 syndrome bits from Z-type stabilizers; their binary value encodes the qubit number (3 = 011 in binary)',
        '6 syndrome bits, one per stabilizer generator',
        '1 syndrome bit indicating an error occurred',
        '7 syndrome bits, one per physical qubit',
    ],
    correct_index=0,
    explanation="The Steane code has 3 Z-type stabilizers. An X error on qubit j anticommutes with each Z stabilizer that includes qubit j. The 3-bit Z syndrome reads out the binary representation of the error qubit index. For example, qubit 3 = 011 in binary triggers stabilizers 1 and 2 (the two LSB stabilizers). This is exactly the Hamming code's single-error-correcting syndrome structure.",
    hints=[
        'The Hamming parity check matrix columns are the binary representations of 1..7.',
    ],
    grade_mode=GradeMode.AUTO,
)
