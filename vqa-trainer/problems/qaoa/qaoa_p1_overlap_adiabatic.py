"""Problem: qaoa_p1_overlap_adiabatic"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='qaoa_p1_overlap_adiabatic',
    category='QAOA',
    difficulty='advanced',
    question='At p=1, how does the QAOA state relate to the adiabatic algorithm, and what limits its performance for general graphs?',
    choices=[
        'p=1 QAOA captures only 1-local correlations (each qubit sees its immediate neighbours), missing multi-hop structure needed for dense or clustered graphs',
        'p=1 QAOA is equivalent to one step of the adiabatic algorithm and always achieves the GW bound',
        'p=1 QAOA has zero overlap with the adiabatic path because the Trotter error is too large',
        'p=1 QAOA is limited by the speed of the classical optimiser, not the quantum circuit',
    ],
    correct_index=0,
    explanation="At p=1, each qubit's U_C(γ) evolution depends on its immediate neighbours, and U_B(β) mixes only local amplitudes. The effective 'light cone' extends 1 hop, so correlations beyond distance 1 in the graph are invisible to the p=1 circuit. For graphs where the optimal cut assignment depends on long-range structure (dense graphs, expanders), p=1 cannot capture this and the approximation ratio is limited. This is why p=1 achieves exactly 0.6924 on 3-regular graphs (local structure is sufficient) but performs poorly on complete graphs (requires long-range correlations).",
    hints=[
        "Think about how far information can propagate in p layers — the 'light cone' is p hops.",
    ],
    grade_mode=GradeMode.MC,
)
