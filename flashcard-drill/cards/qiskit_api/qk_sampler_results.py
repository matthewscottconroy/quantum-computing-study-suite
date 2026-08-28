"""Card: qk_sampler_results"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qk_sampler_results',
    category='Qiskit API',
    front='How do you get counts from a SamplerV2 result?',
    back="result = job.result(); result[0] is the pub result; counts = result[0].data.<creg_name>.get_counts().  The attribute is the classical-register name: 'meas' after measure_all(), 'c' for a default ClassicalRegister.",
)
