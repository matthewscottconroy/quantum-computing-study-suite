"""Problem: bos_gkp_stabilizers"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='bos_gkp_stabilizers',
    category='Bosonic Codes',
    difficulty='intermediate',
    question="The GKP code's stabilizers are displacement operators in phase space. What are they?",
    choices=[
        'S_q = e^{i2√π q̂} and S_p = e^{i2√π p̂} — displacements by 2√π in position and momentum',
        'â†â (photon number) and â (annihilation operator)',
        'e^{iπ q̂²} and e^{iπ p̂²} — squeezing operators',
        'X⊗n and Z⊗n analogues for the oscillator',
    ],
    correct_index=0,
    explanation='The GKP stabilizers are the displacement operators: S_q = e^{i2√π q̂} (displacement by 2√π in position, or equivalently in momentum by 2√π with appropriate convention) and S_p = e^{i2√π p̂}. These operators commute because [q̂, p̂] = i and e^{ia q̂} e^{ib p̂} = e^{iab} e^{ib p̂} e^{ia q̂} — they commute when 2√π · 2√π = 4π gives e^{4πi·phase} = 1. The code space is the simultaneous +1 eigenspace of both stabilizers — the set of oscillator states periodic on a √2π lattice.',
    hints=[
        'GKP stabilizers are phase-space displacements that commute because their product phase is a multiple of 2π.',
    ],
    grade_mode=GradeMode.AUTO,
)
