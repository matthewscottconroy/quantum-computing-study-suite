"""Card: mbp_TEBD"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='mbp_TEBD',
    category='Many-Body Physics',
    front='TEBD algorithm',
    back='Time-Evolving Block Decimation: Trotterises the time-evolution operator and applies it as a sequence of two-site gates to an MPS, truncating bond dimension at each step.',
)
