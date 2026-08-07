"""Problem: rep_detect_vs_correct"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='rep_detect_vs_correct',
    category='Repetition Code',
    difficulty='beginner',
    question='A distance-2 code can detect 1 error but not correct it. A distance-3 code can correct 1 error. Why the difference?',
    choices=[
        'Distance 3 has unique syndromes for each single error; distance 2 only knows an error occurred but not where',
        'Distance 3 uses more qubits, giving it more syndrome bits',
        'Distance 2 cannot distinguish X from Z errors, while distance 3 can',
        'Distance 3 is transversal; distance 2 is not',
    ],
    correct_index=0,
    explanation='Detection requires only that an error takes the state outside the codespace (any non-zero syndrome). Correction requires that different single-error patterns produce distinct syndromes so the decoder can identify and reverse each one. A distance-2 code maps all weight-1 errors to error spaces, but multiple errors may share syndromes or be confused with each other — there is not enough distinguishing information to correct. Distance 3 guarantees all weight-1 error syndromes are unique.',
    hints=[
        "Error correction needs to identify not just 'an error happened' but 'which error happened.'",
    ],
    grade_mode=GradeMode.AUTO,
)
