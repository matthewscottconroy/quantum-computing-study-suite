"""Card: qk_estimator_results"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qk_estimator_results',
    category='Qiskit API',
    front='Where are expectation values in an EstimatorV2 result?',
    back="result[0].data.evs — expectation values (scalar or ndarray matching the broadcast shape) — and result[0].data.stds — standard errors.  For the Bell state, (qc, SparsePauliOp('ZZ')) gives evs = 1.0.",
)
