"""Problem: ansatz_brick_layer_cnot_count"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ansatz_brick_layer_cnot_count',
    category='Ansatz Design',
    difficulty='intermediate',
    question='For an n-qubit circuit with one brick-layer of entangling gates (both even and odd sublayers), how many CNOT gates are used in total?',
    choices=[
        'n-1 — one CNOT per neighbouring pair across the full linear chain',
        'n/2 — only even pairs are coupled',
        '2(n-1) — two CNOTs per CNOT gate (each ZZ rotation needs 2 CNOTs)',
        'n²/4 — all-to-all connectivity scaled by the brick pattern',
    ],
    correct_index=0,
    explanation='On an n-qubit linear chain, the two sublayers together couple all n-1 neighbouring pairs (0,1),(1,2),...,(n-2,n-1) — exactly n-1 CNOT gates total per complete brick-layer cycle. Even sublayer: ⌊n/2⌋ CNOTs; odd sublayer: ⌊(n-1)/2⌋ CNOTs; total = n-1 for any n. This O(n) CNOT count per layer makes brick-layer ansätze hardware-efficient — compare to O(n²) for all-to-all entangling layers.',
    hints=[
        'Count each neighbouring pair: (0,1),(1,2),...,(n-2,n-1) — how many are there?',
    ],
    grade_mode=GradeMode.MC,
)
