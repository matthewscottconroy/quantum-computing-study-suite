"""Card: thm_no_cloning"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='thm_no_cloning',
    category='Theorems',
    front='No-cloning theorem statement',
    back='It is impossible to create an exact copy of an unknown quantum state.  Follows from linearity of QM.',
)
