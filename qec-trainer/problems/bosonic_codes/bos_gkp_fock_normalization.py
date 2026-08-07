"""Problem: bos_gkp_fock_normalization"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='bos_gkp_fock_normalization',
    category='Bosonic Codes',
    difficulty='advanced',
    question='The ideal GKP codewords are superpositions of infinitely many equally-spaced position eigenstates. Why are they not normalizable, and why is the code still well-defined operationally?',
    choices=[
        'Position eigenstates |q⟩ are not normalizable in L²(R); ideal GKP states are mathematical idealizations, but physical GKP states use finitely-squeezed Gaussians and are well-defined experimentally',
        'GKP codewords are normalizable because the Fock basis is complete and orthonormal',
        'The code is ill-defined for this reason and cannot be implemented',
        'Normalization is not required for mixed states, and GKP codewords are always mixed',
    ],
    correct_index=0,
    explanation="Ideal GKP codewords are |0̄⟩ ∝ ∑_{n=-∞}^{∞} |q = 2n√π⟩ — an infinite sum of position eigenstates with delta-function wavefunctions. Position eigenstates |q⟩ are not normalizable (⟨q|q'⟩ = δ(q-q') is a distribution, not an L² function), so the ideal GKP state has infinite norm. In practice, physical GKP states are regularized by replacing delta functions with narrow Gaussians (squeezed states), giving a normalizable state with finitely large but finite norm. These approximate GKP states have been demonstrated experimentally in trapped ions, microwave cavities, and optical systems, and GKP error correction works operationally even for approximate states.",
    hints=[
        'Position eigenstates |q⟩ are Dirac deltas — not square-integrable. Finite squeezing regularizes them.',
    ],
    grade_mode=GradeMode.AUTO,
)
