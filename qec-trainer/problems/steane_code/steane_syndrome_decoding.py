"""Problem: steane_syndrome_decoding"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='steane_syndrome_decoding',
    category='Steane Code',
    difficulty='intermediate',
    question='The Steane code produces a 3-bit syndrome for X errors and a 3-bit syndrome for Z errors. How does the decoder use these?',
    choices=[
        'Each 3-bit syndrome encodes the binary index (1–7) of the erroneous qubit; syndrome 000 means no error',
        'The two syndromes are XORed to find the qubit position',
        'Each syndrome bit tells whether a specific qubit errored or not',
        'The syndromes are averaged to find the most likely error location',
    ],
    correct_index=0,
    explanation="The Steane code's parity check matrix has columns equal to the binary representations of 1 through 7. When a single Z error occurs on qubit j, the 3-bit X syndrome reads out the binary encoding of j (e.g., qubit 3 → syndrome 011 = 3). Syndrome 000 indicates no Z error. Similarly the Z syndrome identifies X error location. This Hamming-code syndrome structure makes single-error correction straightforward.",
    hints=[
        'Hamming codes are designed so the syndrome directly gives the error position in binary.',
    ],
    grade_mode=GradeMode.AUTO,
)
