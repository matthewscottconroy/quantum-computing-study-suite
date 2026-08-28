"""Card: qk_estimator_broadcast"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qk_estimator_broadcast',
    category='Qiskit API',
    front='How does EstimatorV2 broadcast observables and parameters?',
    back='Arrays broadcast numpy-style within one PUB: (qc, [obsA, obsB, obsC]) → evs is a length-3 array; (qc, obs, [[0.0], [π]]) sweeps parameter sets → one ev per binding.  Observable and parameter axes combine by broadcasting rules.',
)
