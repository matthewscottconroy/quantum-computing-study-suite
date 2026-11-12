"""Card: thm_no_deleting"""
from __future__ import annotations
from quantum_study.flashcard_drill.core.models import Flashcard

CARD = Flashcard(
    id='thm_no_deleting',
    category='Theorems',
    front='No-deleting theorem statement',
    back='Given two copies of an unknown state, it is impossible to delete one perfectly (time-reverse of no-cloning)',
)
