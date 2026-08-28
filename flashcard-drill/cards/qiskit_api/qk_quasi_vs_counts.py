"""Card: qk_quasi_vs_counts"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qk_quasi_vs_counts',
    category='Qiskit API',
    front='Quasi-probability distributions vs counts — which primitive version returns which?',
    back='Old V1 Sampler returned QuasiDistribution objects — error mitigation can make entries negative; nearest_probability_distribution() projects back to a true distribution.  SamplerV2 returns raw shot data/counts per classical register instead.',
)
