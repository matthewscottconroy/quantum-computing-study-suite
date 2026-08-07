"""Card: comm_robertson"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='comm_robertson',
    category='Commutators',
    front='Robertson uncertainty relation statement',
    back='For observables A and B: ΔA·ΔB ≥ ½|⟨ψ|[A,B]|ψ⟩|.  Saturated by Gaussian (coherent) states for the canonical pair x̂, p̂.',
)
