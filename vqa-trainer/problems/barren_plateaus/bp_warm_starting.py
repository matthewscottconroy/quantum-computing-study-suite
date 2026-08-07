"""Problem: bp_warm_starting"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='bp_warm_starting',
    category='Barren Plateaus',
    difficulty='intermediate',
    question="Does 'warm starting' (initialising VQE near a known good solution) avoid barren plateaus?",
    choices=[
        'Partially — it avoids the flat region around random initialisation, but if the good solution lies inside a barren plateau region, training will still stall',
        'Yes — any good initialisation completely eliminates barren plateaus by definition',
        'No — barren plateaus affect all parameter regions equally regardless of initialisation',
        'Yes — warm starting from the Hartree-Fock state is always sufficient to escape barren plateaus',
    ],
    correct_index=0,
    explanation='Warm starting from a classically computed approximate solution (e.g. Hartree-Fock, CCSD, or a classical relaxation) can bypass the flat region near random initialisation where barren plateaus are most severe. If the warm start lands near the true minimum, the circuit parameters are in a region with non-negligible gradients and training proceeds. However, warm starting is not a guaranteed fix: if the good solution lies in a region where the ansatz is highly expressive (close to a 2-design), barren plateaus persist. Warm starting is most effective combined with problem-motivated (low-expressibility) ansätze.',
    hints=[
        'Warm starting helps if the target is outside the flat barren plateau region.',
    ],
    grade_mode=GradeMode.MC,
)
