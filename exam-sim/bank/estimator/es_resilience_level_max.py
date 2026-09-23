"""Question: es_resilience_level_max"""
from core.models import Question

QUESTION = Question(
    id='es_resilience_level_max',
    section='Estimator',
    question='What happens?\n\n```python\nfrom qiskit_ibm_runtime import EstimatorV2\n\nestimator = EstimatorV2(mode=backend)\nestimator.options.resilience_level = 3\n```',
    options=[
        'It is accepted and switches on probabilistic error cancellation',
        'It raises a validation error — EstimatorV2 accepts resilience_level 0, 1 or 2 only',
        'It is silently clamped to 2',
        'It is accepted and switches on zero-noise extrapolation plus PEC',
    ],
    correct_index=1,
    explanation='The V2 estimator defines only three levels: 0 (no mitigation), 1 (readout-error mitigation, the default) and 2 (gate-level mitigation, i.e. ZNE). Level 3 was a V1-era spelling for PEC and no longer validates. Anything past level 2 is switched on explicitly through options.resilience, never by a level number.',
    difficulty='hard',
)
