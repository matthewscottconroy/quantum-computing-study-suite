"""Problem: qaoa_approx_ratio_numeric"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='qaoa_approx_ratio_numeric',
    category='QAOA',
    difficulty='intermediate',
    question='A MaxCut QAOA circuit on a 4-edge graph achieves ⟨C⟩ = 2.4. The optimal cut value is 4. What is the approximation ratio?\n\nEnter your numeric answer (decimal, e.g. 0.6).',
    choices=[],
    correct_index=-1,
    correct_value=0.6,
    tolerance=0.0001,
    explanation='Approximation ratio = ⟨C⟩ / C_opt = 2.4 / 4.0 = 0.6. An approximation ratio of 0.6 means the QAOA solution achieves 60% of the optimal cut value. For comparison, the p=1 QAOA on 3-regular graphs achieves ≈0.6924, and the Goemans-Williamson SDP achieves 0.878.',
    hints=[
        'Divide the achieved cost by the optimal cost.',
    ],
    grade_mode=GradeMode.AUTO,
)
