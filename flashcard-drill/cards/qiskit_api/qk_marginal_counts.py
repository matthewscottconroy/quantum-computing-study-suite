"""Card: qk_marginal_counts"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qk_marginal_counts',
    category='Qiskit API',
    front='How do you reduce a counts dict to a subset of bits?',
    back="from qiskit.result import marginal_counts; marginal_counts(counts, indices=[0]) sums over all other bits, keeping only bit 0 (little-endian index) — e.g. {'01': 100} → {'1': 100}.  Useful for analysing one register out of many.",
)
