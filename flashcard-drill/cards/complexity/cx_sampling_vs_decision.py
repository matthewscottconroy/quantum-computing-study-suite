"""Card: cx_sampling_vs_decision"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='cx_sampling_vs_decision',
    category='Complexity',
    front='Sampling tasks vs decision problems for quantum advantage',
    back='Sampling tasks (BosonSampling, IQP, RCS) are easier to demonstrate advantage on hardware but harder to verify classically.  Decision problems (BQP) have cleaner complexity-theoretic foundations.',
)
