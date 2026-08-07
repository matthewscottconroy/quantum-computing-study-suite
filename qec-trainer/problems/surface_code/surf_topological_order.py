"""Problem: surf_topological_order"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='surf_topological_order',
    category='Surface Code',
    difficulty='advanced',
    question='The toric code exhibits topological order. What does this mean physically?',
    choices=[
        "The ground state degeneracy depends only on the topology of the manifold, not on the Hamiltonian's local details",
        'The code is defined on a topologically curved space like a sphere',
        'Errors are corrected using topological invariants of particle paths',
        'The code can only be implemented on hardware with a torus geometry',
    ],
    correct_index=0,
    explanation='Topological order means the degenerate ground subspace cannot be distinguished by any local operator — only global (topological) operations like non-contractible loops can tell the degenerate states apart. For the toric code, the ground state degeneracy is 4-fold on a torus and 1-fold on a sphere — determined purely by the Euler characteristic of the surface. This robustness to local perturbations is what gives topologically ordered systems their error-protection properties.',
    hints=[
        'Topological order: the ground state degeneracy is a topological invariant, not a local property.',
    ],
    grade_mode=GradeMode.AUTO,
)
