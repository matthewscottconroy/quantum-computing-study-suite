"""Problem: surf_rotated_code"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='surf_rotated_code',
    category='Surface Code',
    difficulty='intermediate',
    question='What is the rotated surface code?',
    choices=[
        'A 45° rotation of the lattice that reduces total qubit count to d² (data + ancilla combined)',
        'A surface code rotated in time for better syndrome extraction',
        'A surface code variant that uses only Z stabilizers',
        'A 3D generalization of the surface code',
    ],
    correct_index=0,
    explanation='The rotated surface code is a 45° rotation of the standard toric/surface code lattice. This rotation tiles the plane more efficiently: a distance-d rotated code uses d² data qubits and (d²−1) ancilla qubits — roughly half the overhead of the unrotated version, which requires ~2d² qubits for d logical qubits.',
    hints=[
        'Rotating a square lattice by 45° changes how boundaries and stabilizers are arranged.',
    ],
    grade_mode=GradeMode.AUTO,
)
