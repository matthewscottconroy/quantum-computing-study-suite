"""Problem: surf_toric_code"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='surf_toric_code',
    category='Surface Code',
    difficulty='advanced',
    question='Describe the toric code and explain how it differs from the surface code with open boundaries.',
    choices=[],
    correct_index=-1,
    explanation='The toric code (Kitaev 2003) is defined on a 2D lattice with periodic boundary conditions (a torus topology). It encodes 2 logical qubits per torus. Its stabilizers are the same XXXX plaquette and ZZZZ vertex operators as the surface code, but there are no boundaries. The surface code uses open boundaries (rough and smooth), which break the torus into a disk topology, encoding 1 logical qubit. The boundaries also pin the endpoints of logical string operators. Practically, the surface code is more hardware-friendly because a torus requires non-local connections in any 2D embedding, whereas a surface code patch needs only local nearest-neighbor interactions.',
    hints=[
        'Think about what topological constraints change when a torus is cut open along boundaries.',
    ],
    grade_mode=GradeMode.CLAUDE,
)
