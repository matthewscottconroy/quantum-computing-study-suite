"""Card: qc_equivalence"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qc_equivalence',
    category='Quantum Circuits',
    front='Circuit equivalence: definition',
    back='Two circuits are equivalent iff they implement the same unitary (up to global phase).  Checking equivalence is #P-hard in general.',
)
