"""Problem: surf_boundary_types"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='surf_boundary_types',
    category='Surface Code',
    difficulty='intermediate',
    question='The planar surface code has two types of boundaries. What are they and what do they do?',
    choices=[
        'Rough (smooth Z) boundaries that terminate Z strings, and smooth (rough X) boundaries that terminate X strings',
        'Top and bottom boundaries for encoding and readout respectively',
        'X-only boundaries and Z-only boundaries that provide error correction at the edges',
        'Periodic boundaries on two sides and open boundaries on the other two',
    ],
    correct_index=0,
    explanation="The surface code has 'rough' boundaries (where Z stabilizers on the boundary are weight-2 instead of weight-4) and 'smooth' boundaries (where X stabilizers are weight-2). Logical Z̄ strings terminate on rough boundaries; logical X̄ strings terminate on smooth boundaries. This asymmetry allows the code to encode exactly 1 logical qubit (instead of 2 on a torus).",
    hints=[
        'Boundary conditions determine where logical string operators can start and end.',
    ],
    grade_mode=GradeMode.AUTO,
)
