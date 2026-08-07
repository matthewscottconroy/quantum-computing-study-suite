"""Card: cx_RCS"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='cx_RCS',
    category='Complexity',
    front='Random circuit sampling: why is it hard?',
    back="Output distribution of a random n-qubit circuit anticoncentrates; approximate simulation is conjectured #P-hard, underpinning Google's 2019 supremacy claim",
)
