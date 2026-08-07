"""Card: ec_good_codes"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='ec_good_codes',
    category='Error Correction',
    front='Asymptotically good quantum codes',
    back='[[n, Θ(n), Θ(n)]] codes with linear rate and linear distance exist (Leverrier-Zémor 2022, Dinur et al. 2022).  This resolves a long-standing open problem in quantum coding theory.',
)
