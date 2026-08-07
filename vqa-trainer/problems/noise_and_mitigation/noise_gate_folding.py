"""Problem: noise_gate_folding"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='noise_gate_folding',
    category='Noise & Mitigation',
    difficulty='intermediate',
    question='In ZNE via gate folding, a gate G is replaced by G → G(G†G)^n. By what factor does this amplify the noise?',
    choices=[
        '(2n+1)x — the folded sequence has 2n+1 times as many gates as the original',
        'n x',
        '2^n x',
        'n² x',
    ],
    correct_index=0,
    explanation='Replacing G with G(G†G)^n inserts 2n additional gates (n copies of G†G). The total number of gates acting on that position becomes 2n+1 (original G plus 2n more). Since each gate contributes approximately the same noise, the noise is amplified by (2n+1)x. The logical operation is preserved because G†G = I, so (G†G)^n = I and the unitary action remains G. This provides noise factors λ = 1, 3, 5, 7, ... for n = 0, 1, 2, 3, ...',
    hints=[
        'Count the total number of G and G† applications in the folded sequence.',
    ],
    grade_mode=GradeMode.MC,
)
