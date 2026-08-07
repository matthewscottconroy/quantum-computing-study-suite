"""Card: qi_trace_distance"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qi_trace_distance',
    category='Quantum Info',
    front='Trace distance D(ρ, σ) = ?',
    back='D(ρ, σ) = ½ Tr|ρ - σ|  where |A| = √(A†A)   Ranges [0, 1]',
)
