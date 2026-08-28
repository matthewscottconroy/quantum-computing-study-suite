"""Card: qk_estimator_precision"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qk_estimator_precision',
    category='Qiskit API',
    front="What does the Estimator's precision argument control?",
    back='The target standard error of the expectation-value estimates: estimator.run(pubs, precision=0.01), or per-PUB as the 4th element.  Smaller precision → more shots.  It replaces the shots argument of the Sampler for EstimatorV2.',
)
