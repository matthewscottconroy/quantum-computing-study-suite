"""Problem: steane_x_stabilizers"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='steane_x_stabilizers',
    category='Steane Code',
    difficulty='intermediate',
    question='The Steane code has 3 X-type stabilizers derived from the Hamming [7,4,3] parity check matrix rows. Which of the following is one valid X-type generator?',
    choices=[
        'XIXIXXX (X on qubits 1,3,6,7 — corresponding to Hamming parity check row [1,0,1,0,1,1,0])',
        'XXXXXXX (X on all 7 qubits)',
        'XXXXIII (X on first 4 qubits only)',
        'XZXZXZX (alternating X and Z)',
    ],
    correct_index=0,
    explanation="The Steane code's X-type stabilizers come from the rows of the [7,4,3] Hamming parity check matrix H. The three rows of H (in standard form) correspond to sets of qubit positions; one representative is the set {1,3,5,7} giving XIXIXIX, another is {2,3,6,7} giving IXXIIXX, and {4,5,6,7} giving IIIIXXXX. Each row has weight 4, and the X stabilizer applies X to those qubits. These detect Z errors by anticommuting with Z on any qubit in the support.",
    hints=[
        'The Hamming parity check matrix has rows with exactly 4 ones in a [7,4,3] code.',
    ],
    grade_mode=GradeMode.AUTO,
)
