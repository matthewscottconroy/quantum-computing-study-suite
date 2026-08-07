"""Card: alg_QFT_gates"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='alg_QFT_gates',
    category='Algorithms',
    front='QFT gate count vs classical FFT?',
    back='QFT: O(n²) gates   Classical FFT: O(n 2ⁿ) — exponential advantage in gate count',
)
