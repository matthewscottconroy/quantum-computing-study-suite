"""Problem: surf_anyons"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='surf_anyons',
    category='Surface Code',
    difficulty='advanced',
    question='In the surface code, errors create pairs of excitations. These excitations are:',
    choices=[
        'Anyons (e and m type)',
        'Fermions',
        'Majorana modes',
        'Photons',
    ],
    correct_index=0,
    explanation="X errors create pairs of 'e' (electric) anyons at Z-stabilizer plaquettes. Z errors create pairs of 'm' (magnetic) anyons at X-stabilizer plaquettes. Decoding means matching and annihilating anyon pairs by minimum weight matching.",
    hints=[
        "The surface code is related to Kitaev's toric code and topological order.",
    ],
    grade_mode=GradeMode.AUTO,
)
