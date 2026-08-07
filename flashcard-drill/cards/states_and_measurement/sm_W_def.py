"""Card: sm_W_def"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='sm_W_def',
    category='States & Measurement',
    front='W state definition',
    back='|W⟩ = (|100...0⟩ + |010...0⟩ + ... + |000...1⟩)/√n  — robust entanglement; partial trace retains entanglement unlike GHZ',
)
