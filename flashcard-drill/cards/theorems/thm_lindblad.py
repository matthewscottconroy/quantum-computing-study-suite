"""Card: thm_lindblad"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='thm_lindblad',
    category='Theorems',
    front='Lindblad theorem (GKSL)',
    back='The most general Markovian master equation is dρ/dt = −i[H,ρ] + Σₖ(LₖρLₖ† − ½{Lₖ†Lₖ,ρ}).  Guaranteed completely positive and trace-preserving.',
)
