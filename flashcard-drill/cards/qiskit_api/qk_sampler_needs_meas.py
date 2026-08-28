"""Card: qk_sampler_needs_meas"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qk_sampler_needs_meas',
    category='Qiskit API',
    front='What happens if you give SamplerV2 a circuit without measurements?',
    back="The Sampler samples classical registers, so a circuit with no measurements yields an empty DataBin (StatevectorSampler warns: 'circuit has no output classical registers').  Always add measure()/measure_all() before sampling.",
)
