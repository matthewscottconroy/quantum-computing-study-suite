"""Problem: surf_spacetime_diagram"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='surf_spacetime_diagram',
    category='Surface Code',
    difficulty='intermediate',
    question='In surface code decoding, d rounds of syndrome measurement create a 3D syndrome history. What shape is the decoding graph?',
    choices=[
        'A d×d×d cube (space × space × time), where syndrome defects are vertices matched in 3D',
        'A 2D grid extended only in space — time is averaged out',
        'A 1D chain encoding the time sequence of syndrome changes',
        'A d×d plane per time step, decoded independently each round',
    ],
    correct_index=0,
    explanation='With d rounds of (noisy) syndrome measurement, the full syndrome history forms a 3D hypercubic graph: two spatial dimensions (the d×d lattice) and one temporal dimension (d rounds). Syndrome defects appear as vertices in this 3D graph. A qubit error appears as a persistent defect across multiple time steps; a measurement error appears as a defect at only one time step. The 3D MWPM decoder matches defect pairs in this space-time graph, simultaneously handling both qubit errors and measurement errors.',
    hints=[
        'Time is the third dimension: qubit errors persist; measurement errors are transient.',
    ],
    grade_mode=GradeMode.AUTO,
)
