"""Problem: ft_solovay_kitaev"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ft_solovay_kitaev',
    category='Fault Tolerance',
    difficulty='advanced',
    question='The Solovay-Kitaev theorem guarantees that any single-qubit gate can be approximated to precision ε using Clifford+T. Approximately how many T gates are required?',
    choices=[
        'O(log^c(1/ε)) T gates for some constant c ≈ 3–4',
        'O(1/ε) T gates — linear in the precision',
        'O(log(1/ε)) T gates — logarithmic with a small constant',
        'Exponential in 1/ε',
    ],
    correct_index=0,
    explanation='The Solovay-Kitaev theorem proves that any SU(2) gate can be approximated to precision ε using O(log^c(1/ε)) gates from a universal finite gate set (e.g., Clifford+T), where c ≈ 3.97 in the original proof. Optimized decomposition algorithms (e.g., Ross-Selinger for T-count optimization) achieve T-count ~3log₂(1/ε) + O(log log(1/ε)). This means each approximate rotation in a quantum algorithm translates to ~30–50 T gates for ε ~ 10^{-10} precision, making T-count estimates crucial for full fault-tolerant resource counts.',
    hints=[
        'S-K theorem: polylogarithmic approximation — not linear, not exponential.',
    ],
    grade_mode=GradeMode.AUTO,
)
