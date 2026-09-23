"""Question: es_pub_wrong_order"""
from core.models import Question

QUESTION = Question(
    id='es_pub_wrong_order',
    section='Estimator',
    question='One of these four calls raises `TypeError: Invalid observable type: <class \'float\'>`. Which one?\n\n```python\ntheta = Parameter("t")\nqc = QuantumCircuit(1)\nqc.ry(theta, 0)\nest = StatevectorEstimator()\n```',
    options=[
        'est.run([(qc, SparsePauliOp("Z"), [np.pi])])',
        'est.run([(qc, "Z", {theta: np.pi})])',
        'est.run([(qc, [np.pi], SparsePauliOp("Z"))])',
        'est.run([(qc, [SparsePauliOp("Z")], [np.pi])])',
    ],
    correct_index=2,
    explanation='An estimator pub is ordered (circuit, observables, parameter_values). Swapping the last two makes the estimator try to coerce the float π into an observable. The other three are all legal: parameter values may be a sequence or a {Parameter: value} mapping, and wrapping the observable in a list simply gives evs of shape (1,) instead of shape ().',
    difficulty='hard',
)
