"""Question: es_broadcast"""
from core.models import Question

QUESTION = Question(
    id='es_broadcast',
    section='Estimator',
    question='What is the shape/content of `evs`?\n\n```python\nqc = QuantumCircuit(1)\nqc.h(0)\nobs = [SparsePauliOp("X"), SparsePauliOp("Z")]\nevs = StatevectorEstimator().run([(qc, obs)]).result()[0].data.evs\n```',
    options=[
        'An array of two values: [1.0, 0.0] — one expectation value per observable',
        'A single averaged value 0.5',
        'It raises an error — one pub may only carry one observable',
        'A 2x2 matrix of covariances',
    ],
    correct_index=0,
    explanation="A pub's observables broadcast like numpy arrays: a list of two observables yields evs of shape (2,), evaluated on the same state — here ⟨X⟩ = 1 and ⟨Z⟩ = 0 for |+⟩. Nothing is averaged.",
    difficulty='medium',
)
