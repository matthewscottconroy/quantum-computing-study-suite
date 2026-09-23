"""Question: ra_quasi_dist_negative"""
from core.models import Question

QUESTION = Question(
    id='ra_quasi_dist_negative',
    section='Results analysis',
    question='Which statement about quasi-probability distributions is TRUE?',
    options=[
        'Their values can be negative, which is why error-mitigated output is reported as quasi-probabilities rather than counts',
        'They are just counts divided by shots, so every value lies in [0, 1]',
        'They are what SamplerV2 returns from result[0].data.meas.quasi_dists',
        'They always sum to a number greater than 1 because of readout error',
    ],
    correct_index=0,
    explanation='A quasi-probability distribution sums to 1 but may contain NEGATIVE entries — that is exactly what lets techniques such as measurement-error mitigation and probabilistic error cancellation invert a noise map. The V1 Sampler exposed them as `result.quasi_dists`; SamplerV2 removed that field and returns raw per-shot bits (BitArray) instead, leaving mitigation to explicit post-processing.',
    difficulty='medium',
)
