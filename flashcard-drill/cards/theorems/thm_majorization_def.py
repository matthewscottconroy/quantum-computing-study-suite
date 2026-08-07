"""Card: thm_majorization_def"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='thm_majorization_def',
    category='Theorems',
    front='Majorization condition λ ≺ μ definition',
    back="λ ≺ μ iff Σᵢ₌₁ᵏ λ↓ᵢ ≤ Σᵢ₌₁ᵏ μ↓ᵢ for all k, with equality for k = n.  Quantifies 'more uniform' distributions.",
)
