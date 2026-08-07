"""Card: qi_purity"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qi_purity',
    category='Quantum Info',
    front='Purity of ρ',
    back='γ = Tr(ρ²)   Ranges [1/d, 1].  γ=1 iff ρ is pure.',
)
