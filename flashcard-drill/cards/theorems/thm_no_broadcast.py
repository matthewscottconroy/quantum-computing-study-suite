"""Card: thm_no_broadcast"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='thm_no_broadcast',
    category='Theorems',
    front='No-broadcasting theorem',
    back='A mixed quantum state cannot be broadcast (copied to a product state) — generalises no-cloning to mixed states',
)
