"""Problem: qaoa_cnot_scaling"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='qaoa_cnot_scaling',
    category='QAOA',
    difficulty='intermediate',
    question='How does the number of CNOT gates in a MaxCut QAOA circuit scale with circuit depth p and the number of graph edges |E|?',
    choices=[
        'O(p·|E|) — each of the p problem-unitary layers applies one ZZ-rotation (2 CNOTs) per edge',
        'O(p·n) where n is the number of nodes — mixer layers dominate',
        'O(p²·|E|) — pairs of layers interfere requiring quadratic gate count',
        'O(|E|) — only one layer of problem unitaries is needed regardless of p',
    ],
    correct_index=0,
    explanation='Each layer of U_C(γ) applies e^{-iγ(1-ZᵤZᵥ)/2} for every edge (u,v)∈E. Each ZZ-rotation requires 2 CNOT gates (CNOT-Rz-CNOT). So one layer uses 2|E| CNOTs. With p layers the total is 2p|E| = O(p|E|) CNOTs. The mixer layers U_B(β) use single-qubit Rx gates — no CNOTs. For dense graphs (|E|=O(n²)), the CNOT count is O(pn²) which can be prohibitive on hardware with limited connectivity.',
    hints=[
        'Count CNOTs per layer: each edge requires 2 CNOTs for the ZZ rotation.',
    ],
    grade_mode=GradeMode.MC,
)
