"""Card: thm_stinespring"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='thm_stinespring',
    category='Theorems',
    front='Stinespring dilation theorem',
    back='Every CPTP map ε on system A can be written as ε(ρ) = Tr_E[U(ρ⊗|0⟩⟨0|)U†] for some unitary U on A⊗E',
)
