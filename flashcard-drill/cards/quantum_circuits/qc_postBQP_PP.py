"""Card: qc_postBQP_PP"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qc_postBQP_PP',
    category='Quantum Circuits',
    front='PostBQP = PP (post-selection and circuits)',
    back='A quantum circuit allowed to post-select on any measurement outcome can simulate any PP computation — and PP can simulate it.  Implies post-selection makes quantum and classical exponentially more powerful.',
)
