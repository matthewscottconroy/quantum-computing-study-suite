"""Problem: surf_syndrome_rounds"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='surf_syndrome_rounds',
    category='Surface Code',
    difficulty='intermediate',
    question='How many rounds of syndrome measurement are needed for reliable decoding in a distance-d surface code?',
    choices=[
        'd rounds (to suppress measurement errors as well as physical errors)',
        '1 round (a single perfect measurement suffices)',
        'd² rounds',
        '2 rounds (one for X, one for Z stabilizers)',
    ],
    correct_index=0,
    explanation='Syndrome measurements are themselves noisy. A single faulty measurement could trigger a wrong correction. By repeating d rounds of measurement, a measurement error appears as a transient event in the space-time syndrome history and can be distinguished from a persistent physical qubit error. The decoder operates on a 3D (space × time) syndrome graph.',
    hints=[
        'Measurement errors look like short events in time; qubit errors persist across rounds.',
    ],
    grade_mode=GradeMode.AUTO,
)
