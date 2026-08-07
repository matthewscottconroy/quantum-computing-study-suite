"""Card: qi_BB84"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qi_BB84',
    category='Quantum Info',
    front='BB84 protocol states and security',
    back='Alice sends one of 4 states: |0⟩,|1⟩ (Z basis) or |+⟩,|−⟩ (X basis) chosen randomly.  Bob measures in random basis; keep only matching-basis results.  Security guaranteed by no-cloning.',
)
