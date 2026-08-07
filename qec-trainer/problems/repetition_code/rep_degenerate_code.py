"""Problem: rep_degenerate_code"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='rep_degenerate_code',
    category='Repetition Code',
    difficulty='advanced',
    question='What is a degenerate quantum code? Can the repetition code perspective illustrate this?',
    choices=[
        'A code where distinct errors produce the same syndrome and same logical effect — they are equivalent',
        'A code with fewer syndromes than error types, causing uncorrectable errors',
        'A code whose stabilizer group contains operators of all weights',
        'A code that corrects fewer errors than the Hamming bound predicts',
    ],
    correct_index=0,
    explanation='A degenerate code allows multiple distinct errors to map to the same syndrome and the same error space, so they can all be corrected by the same recovery. For example, in a distance-5 code, two different weight-2 errors might produce the same syndrome; as long as they have the same effect on the codespace (both are equivalent to the same stabilizer times a logical operator), they are correctable with a single recovery. The 3-qubit code is not degenerate — each single-qubit error has a unique syndrome. Degenerate codes can potentially exceed the quantum Hamming bound.',
    hints=[
        'Think about two errors that produce the same syndrome — can both be corrected?',
    ],
    grade_mode=GradeMode.AUTO,
)
