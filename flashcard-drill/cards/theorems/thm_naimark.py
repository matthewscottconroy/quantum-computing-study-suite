"""Card: thm_naimark"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='thm_naimark',
    category='Theorems',
    front="Naimark's dilation theorem",
    back='Every POVM {Mᵢ} on ℋ can be realised as a projective measurement on a larger Hilbert space ℋ⊗ℋ_ancilla',
)
