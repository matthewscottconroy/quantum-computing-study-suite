"""Problem: bos_gkp_def"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='bos_gkp_def',
    category='Bosonic Codes',
    difficulty='intermediate',
    question='The GKP (Gottesman-Kitaev-Preskill) code encodes a qubit into:',
    choices=[
        'A grid of states evenly spaced in phase space (position and momentum), with codewords being superpositions of squeezed states on a lattice',
        'The Fock states |0⟩ and |2⟩ of a harmonic oscillator',
        'Two coherent states |α⟩ and |−α⟩ like the cat qubit',
        'A two-mode entangled oscillator state for enhanced protection',
    ],
    correct_index=0,
    explanation='The GKP code (2001) encodes a logical qubit into a single oscillator using states that form a 2D lattice in phase space (position q̂ and momentum p̂). The logical |0̄⟩ and |1̄⟩ are superpositions of infinitely many equally spaced position-space delta functions (idealized) or, in practice, superpositions of finitely squeezed Gaussian states on the lattice with spacing √π (or √2π depending on convention). This lattice structure enables correction of small displacement errors in both q and p, analogous to how a classical lattice code corrects small translations.',
    hints=[
        'GKP codes use a lattice structure in phase space — think of a grid of Gaussian peaks.',
    ],
    grade_mode=GradeMode.AUTO,
)
