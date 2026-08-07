"""Problem: rep_weight2_uncorrectable"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='rep_weight2_uncorrectable',
    category='Repetition Code',
    difficulty='intermediate',
    question='In the 3-qubit bit-flip code, what happens if qubits 1 AND 3 both flip (a weight-2 error)?',
    choices=[
        'Syndrome (1,1): qubit 2 appears to be the culprit — wrong correction causes a logical error',
        'The code detects and corrects the error correctly',
        'Syndrome (0,0): no error is detected',
        'Syndrome (1,0): only qubit 1 is identified',
    ],
    correct_index=0,
    explanation='If qubits 1 and 3 flip, Z1Z2 measures -1 and Z2Z3 measures -1, giving syndrome (1,1). This points to qubit 2 — the decoder corrects the wrong qubit, leaving all three flipped and causing a logical X error. Weight-2 errors exceed the correction capacity of d=3.',
    hints=[
        'Weight-2 errors are beyond the correction capacity of a d=3 code.',
    ],
    grade_mode=GradeMode.AUTO,
)
