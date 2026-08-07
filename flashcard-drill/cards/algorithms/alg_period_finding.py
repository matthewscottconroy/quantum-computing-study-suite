"""Card: alg_period_finding"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='alg_period_finding',
    category='Algorithms',
    front='Period finding via QFT',
    back='Prepare superposition Σₓ|x⟩|aˣ mod N⟩, measure second register, then apply QFT to first register.  Peaks at multiples of N/r reveal period r.',
)
