"""Card: qi_subadditivity"""
from __future__ import annotations
from quantum_study.flashcard_drill.core.models import Flashcard

CARD = Flashcard(
    id='qi_subadditivity',
    category='Quantum Info',
    front='Subadditivity of von Neumann entropy',
    back='S(AB) ≤ S(A) + S(B)   — equality iff ρ_AB = ρ_A ⊗ ρ_B (product state)',
)
