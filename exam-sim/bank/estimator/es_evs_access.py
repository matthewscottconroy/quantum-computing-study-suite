"""Question: es_evs_access"""
from core.models import Question

QUESTION = Question(
    id='es_evs_access',
    section='Estimator',
    question='After `result = estimator.run([(qc, obs)]).result()`, where do the expectation values live?',
    options=[
        'result[0].data.evs',
        'result.values[0]',
        'result[0].expectation_value',
        'result[0].data.meas.get_counts()',
    ],
    correct_index=0,
    explanation='Each estimator pub result stores its expectation values in data.evs (a numpy array shaped by observable broadcasting) with matching data.stds. result.values was the V1 access pattern, and counts belong to samplers, not estimators.',
    difficulty='medium',
)
