"""Problem: surf_toric_definition"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='surf_toric_definition',
    category='Surface Code',
    difficulty='intermediate',
    question='The toric code (Kitaev 2003) is defined on a square lattice with periodic boundary conditions. How many logical qubits does it encode?',
    choices=[
        '2 logical qubits — one for each non-contractible loop direction on the torus',
        '1 logical qubit — same as the planar surface code',
        '4 logical qubits — one per corner of the lattice',
        '0 logical qubits — it is a stabilizer state, not a code',
    ],
    correct_index=0,
    explanation='The torus has two topologically independent non-contractible loops (around the two handles). Each pair of such loops (one X-type, one Z-type) supports an independent logical qubit. The toric code on a d×d torus encodes 2 logical qubits: logical X₁ and Z₁ run horizontally and vertically for the first qubit; X₂ and Z₂ for the second. This topological ground state degeneracy (4-fold for 2 qubits) is robust against local perturbations — the hallmark of topological order.',
    hints=[
        'A torus has two independent non-contractible loops — each corresponds to a logical qubit.',
    ],
    grade_mode=GradeMode.AUTO,
)
