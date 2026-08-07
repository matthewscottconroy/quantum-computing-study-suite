"""Problem: surf_percolation"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='surf_percolation',
    category='Surface Code',
    difficulty='advanced',
    question='The surface code threshold is related to a percolation threshold on the lattice. What is the connection?',
    choices=[
        'At the threshold, error chains form a spanning cluster from one boundary to the other — analogous to the percolation transition on the lattice',
        'Percolation theory gives an upper bound on the threshold',
        'The Union-Find decoder uses percolation algorithms directly',
        'Errors percolate through the syndrome graph regardless of the error rate',
    ],
    correct_index=0,
    explanation='The code capacity threshold for the surface code (~10.9%) can be mapped to a bond percolation problem on the lattice. Below the threshold, errors form finite clusters that the decoder can match locally. At the threshold, error chains percolate across the lattice — connecting one boundary to the other — causing logical errors with probability ~1/2. Above threshold, error chains percolate with near-certainty, creating uncorrectable logical errors. The 10.9% value matches the bond percolation threshold of the square lattice (~50% with code-specific corrections).',
    hints=[
        'Below threshold: finite error clusters; above threshold: spanning error chains — this is percolation.',
    ],
    grade_mode=GradeMode.AUTO,
)
