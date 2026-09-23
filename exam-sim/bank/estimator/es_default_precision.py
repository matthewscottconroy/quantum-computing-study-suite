"""Question: es_default_precision"""
from core.models import Question

QUESTION = Question(
    id='es_default_precision',
    section='Estimator',
    question='For `qc` preparing H|0⟩, what are `a` and `b`?\n\n```python\nest = StatevectorEstimator(default_precision=0.2, seed=1)\na = est.run([(qc, "Z")]).result()[0].data.evs\nb = est.run([(qc, "Z")], precision=0.0).result()[0].data.evs\n```',
    options=[
        'a carries Gaussian noise of scale 0.2; b is exactly 0.0 because the per-run precision overrides the constructor default',
        'Both are exactly 0.0 — StatevectorEstimator ignores precision entirely',
        'Both carry noise of scale 0.2 — the constructor default always wins',
        'b raises ValueError: precision must be greater than zero',
    ],
    correct_index=0,
    explanation='run(precision=...) overrides default_precision for that job; the constructor value applies only when run() passes None. For the exact statevector primitive precision 0 means no sampling noise at all, so b is the analytic 0.0. A shot-based estimator such as BackendEstimatorV2 does reject precision=0, since it would imply infinite shots.',
    difficulty='medium',
)
