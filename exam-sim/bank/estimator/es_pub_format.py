"""Question: es_pub_format"""
from core.models import Question

QUESTION = Question(
    id='es_pub_format',
    section='Estimator',
    question='What is the correct way to ask a V2 estimator for the expectation value of observable `obs` on circuit `qc`?',
    options=[
        'estimator.run([(qc, obs)])',
        'estimator.run(qc, obs)',
        'estimator.run([qc], observables=[obs])',
        'estimator.evaluate(qc, obs)',
    ],
    correct_index=0,
    explanation='V2 estimator pubs are tuples of (circuit, observables[, parameter_values]) passed as a list. Positional circuit-plus-observable arguments and the observables= keyword belong to the removed V1 interface; evaluate() has never existed.',
    difficulty='easy',
)
