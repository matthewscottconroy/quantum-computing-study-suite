"""Problem: noise_open_zne_vs_pec"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='noise_open_zne_vs_pec',
    category='Noise & Mitigation',
    difficulty='advanced',
    question='In 3–5 sentences, describe when ZNE is more practical than PEC and vice versa.',
    choices=[],
    correct_index=-1,
    explanation='ZNE is more practical when: a noise model is unavailable (ZNE requires only the ability to amplify noise via gate folding); circuits are moderate depth so the extrapolation error is manageable; or rapid prototyping is needed since ZNE has minimal classical overhead. PEC is preferable when: a detailed noise model (process tomography data) is available; one needs unbiased estimates (ZNE has systematic extrapolation bias); or when noise is gate-specific and structured, making accurate quasi-probability decompositions feasible. In practice, ZNE is the more widely deployed technique on current devices due to its simplicity, while PEC is used in research settings requiring rigorous unbiased estimation at the cost of exponentially higher shot overhead.',
    hints=[
        'Consider availability of noise models, bias vs variance, and practical shot budgets.',
    ],
    grade_mode=GradeMode.CLAUDE,
)
