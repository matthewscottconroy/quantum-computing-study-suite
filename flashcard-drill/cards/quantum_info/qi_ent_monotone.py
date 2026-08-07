"""Card: qi_ent_monotone"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qi_ent_monotone',
    category='Quantum Info',
    front='Entanglement monotone definition',
    back='A function E(ρ) that is non-increasing on average under LOCC: E(ρ) ≥ Σᵢ pᵢ E(σᵢ) where {pᵢ, σᵢ} is the post-LOCC ensemble.',
)
