"""Card: qi_rel_entropy"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qi_rel_entropy',
    category='Quantum Info',
    front='Quantum relative entropy D(ρ||σ) = ?',
    back='D(ρ||σ) = Tr(ρ log ρ) - Tr(ρ log σ) = -S(ρ) - Tr(ρ log σ)   Non-negative; zero iff ρ=σ',
)
