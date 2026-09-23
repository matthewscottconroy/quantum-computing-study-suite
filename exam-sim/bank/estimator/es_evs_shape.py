"""Question: es_evs_shape"""
from core.models import Question

QUESTION = Question(
    id='es_evs_shape',
    section='Estimator',
    question='What does this print?\n\n```python\nqc = QuantumCircuit(1)\nqc.h(0)\nresult = StatevectorEstimator().run([(qc, "Z")]).result()\nprint(result[0].data.evs.shape)\n```',
    options=[
        '(1,)',
        '()',
        '(1, 1)',
        'AttributeError — evs is a Python float, not an array',
    ],
    correct_index=1,
    explanation='evs is always a numpy array whose shape comes from broadcasting the observables against the parameter values. One circuit, one bare observable and no sweep give a 0-d array, so the shape is the empty tuple; float(evs) or evs.item() pulls the number out. Passing ["Z"] instead would have produced shape (1,).',
    difficulty='medium',
)
