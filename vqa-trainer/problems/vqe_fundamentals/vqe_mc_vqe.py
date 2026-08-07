"""Problem: vqe_mc_vqe"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='vqe_mc_vqe',
    category='VQE Fundamentals',
    difficulty='advanced',
    question='What is multistate contracted VQE (MC-VQE)?',
    choices=[
        'Optimises a contracted superposition of multiple VQE states simultaneously to find a set of near-degenerate eigenstates more efficiently',
        'Runs VQE independently on multiple quantum processors and contracts the results classically',
        'Applies a multi-reference contracted CI approach where each reference is a VQE state',
        'A VQE variant that contracts the ansatz depth by merging adjacent parameterised layers',
    ],
    correct_index=0,
    explanation='MC-VQE (Parrish & McMahon 2019) prepares a set of states {|ψₖ(θ)⟩} using a shared parameterised circuit, then diagonalises the Hamiltonian in the subspace spanned by these states. The cost function optimises all states jointly, with the classical diagonalisation step extracting multiple eigenvalues at once. This is efficient when several states (e.g. in a conical intersection) are energetically close and a single contracted ansatz can capture them all with fewer parameters than independent VQE runs.',
    hints=[
        'MC-VQE solves for several states simultaneously using a shared parameterised circuit.',
    ],
    grade_mode=GradeMode.MC,
)
