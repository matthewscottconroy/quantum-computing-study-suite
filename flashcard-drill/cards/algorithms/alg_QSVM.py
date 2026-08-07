"""Card: alg_QSVM"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='alg_QSVM',
    category='Algorithms',
    front='Quantum SVM / quantum ML speedup',
    back='HHL-based QSVM claims exponential speedup in n for training, but requires QRAM and full quantum state access — dequantized classical algorithms match in many cases',
)
