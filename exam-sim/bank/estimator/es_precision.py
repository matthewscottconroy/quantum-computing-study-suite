"""Question: es_precision"""
from core.models import Question

QUESTION = Question(
    id='es_precision',
    section='Estimator',
    question='By default (no precision given), what does StatevectorEstimator return for ⟨Z⟩ of H|0⟩, and what changes if you pass precision=0.1 to run()?',
    options=[
        'Exactly 0.0 by default; with precision=0.1 the value carries simulated shot noise of that scale',
        'A shot-noise estimate by default; precision=0.1 makes it exact',
        'Always exactly 0.0 — precision is ignored by statevector simulation',
        'It raises an error unless precision is specified',
    ],
    correct_index=0,
    explanation="StatevectorEstimator's default precision is 0, meaning exact expectation values from the statevector. A nonzero target precision makes it add Gaussian noise consistent with that standard error, mimicking finite-shot estimation on hardware.",
    difficulty='hard',
)
