"""Card: sm_kochen_specker"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='sm_kochen_specker',
    category='States & Measurement',
    front='Kochen-Specker theorem: statement',
    back='In a Hilbert space of dimension ≥ 3, quantum observables cannot be assigned pre-existing definite values consistently with all measurement contexts (contextuality).',
)
