"""Problem: rep_error_discretization"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='rep_error_discretization',
    category='Repetition Code',
    difficulty='intermediate',
    question='Why is it sufficient to consider only Pauli errors {I, X, Y, Z} when analyzing quantum error correction, even though physical errors are continuous rotations?',
    choices=[
        'Syndrome measurement projects any error into the Pauli basis, discretizing it into a correctable Pauli',
        'Physical hardware can only produce Pauli errors',
        'The quantum Zeno effect suppresses non-Pauli errors between measurements',
        'The Knill-Laflamme conditions only apply to discrete errors',
    ],
    correct_index=0,
    explanation='Any single-qubit error can be written as E = aI + bX + cY + dZ. When syndrome measurement is performed, the state is projected into one of the error subspaces corresponding to I, X, Y, or Z on each qubit. This collapse discretizes the continuous error into one of the four Pauli operators — whichever eigenspace is selected by the syndrome measurement. If the code corrects all Pauli errors, it therefore corrects all physical errors by this discretization argument.',
    hints=[
        'What does syndrome measurement do to a superposition of different error types?',
    ],
    grade_mode=GradeMode.AUTO,
)
