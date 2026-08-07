"""Card: alg_QFT_output"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='alg_QFT_output',
    category='Algorithms',
    front='What does QFT output?',
    back='QFT|j⟩ = (1/√N) Σₖ e^{2πijk/N}|k⟩  — quantum analogue of the DFT',
)
