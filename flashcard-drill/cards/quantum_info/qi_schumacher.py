"""Card: qi_schumacher"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qi_schumacher',
    category='Quantum Info',
    front='Schumacher data compression rate',
    back="Optimal compression of n copies of ρ requires ~n·S(ρ) qubits — quantum analogue of Shannon's source coding theorem",
)
