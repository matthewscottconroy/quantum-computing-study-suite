"""Question: es_broadcast_shape_2d"""
from core.models import Question

QUESTION = Question(
    id='es_broadcast_shape_2d',
    section='Estimator',
    question='What does this print?\n\n```python\ntheta = Parameter("t")\nqc = QuantumCircuit(1)\nqc.ry(theta, 0)\n\nobs  = [[SparsePauliOp("Z")], [SparsePauliOp("X")]]   # shape (2, 1)\nvals = [[0.0, np.pi / 2, np.pi]]                      # shape (1, 3)\n\nevs = StatevectorEstimator().run([(qc, obs, vals)]).result()[0].data.evs\nprint(evs.shape)\n```',
    options=[
        '(3, 2)',
        '(6,)',
        'ValueError — observables and parameter values must have identical shapes',
        '(2, 3)',
    ],
    correct_index=3,
    explanation='Observables and parameter values broadcast against each other exactly like numpy arrays: (2, 1) against (1, 3) gives (2, 3), i.e. every observable evaluated at every parameter point inside a single pub. The shapes only have to be broadcast-compatible, not equal, and the result keeps that shape rather than flattening.',
    difficulty='hard',
)
