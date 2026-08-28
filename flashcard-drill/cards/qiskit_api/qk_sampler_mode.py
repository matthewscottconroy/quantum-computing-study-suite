"""Card: qk_sampler_mode"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qk_sampler_mode',
    category='Qiskit API',
    front='What does the mode= argument of runtime SamplerV2/EstimatorV2 accept?',
    back='A Backend (job mode), a Session, or a Batch object — this selects the execution mode: Sampler(mode=backend), Sampler(mode=session), Sampler(mode=batch).  It replaced the older backend=/session= arguments.',
)
