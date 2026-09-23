"""Question: es_resilience_level_1"""
from core.models import Question

QUESTION = Question(
    id='es_resilience_level_1',
    section='Estimator',
    question='A Runtime EstimatorV2 job runs with its default resilience_level of 1. What mitigation is applied?',
    options=[
        'None — level 1 is a no-op kept for compatibility',
        'Zero-noise extrapolation over noise factors 1, 3 and 5',
        'Measurement/readout error mitigation (twirled readout error extinction)',
        'Probabilistic error cancellation with a capped sampling overhead',
    ],
    correct_index=2,
    explanation='Level 0 is no mitigation, level 1 adds cheap readout-error mitigation (TREX: measurement twirling plus a classical correction) and level 2 adds gate-level mitigation, i.e. ZNE. Readout mitigation is the default because it costs almost nothing in extra sampling.',
    difficulty='medium',
)
