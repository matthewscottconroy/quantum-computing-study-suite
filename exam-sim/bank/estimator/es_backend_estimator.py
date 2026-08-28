"""Question: es_backend_estimator"""
from core.models import Question

QUESTION = Question(
    id='es_backend_estimator',
    section='Estimator',
    question='Which class provides the V2 estimator interface on top of an arbitrary backend object (e.g. a noisy AerSimulator)?',
    options=[
        'BackendEstimatorV2',
        'StatevectorEstimator(backend=...)',
        'AerEstimatorV1',
        'RuntimeEstimator',
    ],
    correct_index=0,
    explanation='BackendEstimatorV2 wraps any BackendV2, decomposing observables into measurable circuits and estimating from shots. StatevectorEstimator takes no backend (always local exact simulation); the other names are not qiskit.primitives classes.',
    difficulty='medium',
)
