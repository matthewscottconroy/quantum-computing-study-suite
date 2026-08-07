"""Card: thm_klein_inequality"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='thm_klein_inequality',
    category='Theorems',
    front="Klein's inequality",
    back='Tr(ρ log ρ − ρ log σ) ≥ 0 for any states ρ, σ — equivalent to non-negativity of quantum relative entropy D(ρ‖σ) ≥ 0.',
)
