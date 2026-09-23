"""Question: sa_pub_forms"""
from core.models import Question

QUESTION = Question(
    id='sa_pub_forms',
    section='Sampler',
    question='Which of these is NOT a valid PUB for SamplerV2.run()?',
    options=[
        '(circuit, observable, parameter_values)',
        'circuit',
        '(circuit, parameter_values)',
        '(circuit, parameter_values, shots)',
    ],
    correct_index=0,
    explanation='A sampler PUB is (circuit, parameter_values, shots) with the last two optional, and a bare circuit is accepted as shorthand for a one-element tuple. Observables belong to *Estimator* PUBs — (circuit, observables, parameter_values, precision) — because a sampler returns measurement samples, not expectation values.',
    difficulty='medium',
)
