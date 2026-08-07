"""Problem: ansatz_uccsd_param_count"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ansatz_uccsd_param_count',
    category='Ansatz Design',
    difficulty='advanced',
    question='Approximately how many parameters does UCCSD have for n total spin-orbitals with nₒ occupied and nᵥ = n-nₒ virtual orbitals?',
    choices=[
        'nₒ·nᵥ single excitations + nₒ²·nᵥ²/4 double excitations (dominant term O(n⁴))',
        '2n parameters — one for each spin-orbital',
        'n² parameters — one for each pair of spin-orbitals',
        'nₒ·nᵥ parameters only — doubles are subsumed by products of singles',
    ],
    correct_index=0,
    explanation='UCCSD includes: (1) singles T₁ = Σ_{ia} t_{ia} a†_a a_i — one parameter per occupied-virtual pair: nₒ·nᵥ parameters; (2) doubles T₂ = Σ_{ijab} t_{ijab} a†_a a†_b a_j a_i — one per pair of occupied (i,j) and virtual (a,b): C(nₒ,2)·C(nᵥ,2) ≈ nₒ²nᵥ²/4 parameters. The doubles term dominates and grows as O(n⁴) — for 20 spin-orbitals with 10 occupied that is ~2500 parameters. This explains why UCCSD circuits are deep and the motivation for active space truncation and ADAPT-VQE which selects a sparse subset.',
    hints=[
        "Doubles involve choosing 2 occupied and 2 virtual orbitals — that's a combinatorial count.",
    ],
    grade_mode=GradeMode.MC,
)
