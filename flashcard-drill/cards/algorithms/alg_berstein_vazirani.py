"""Card: alg_berstein_vazirani"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='alg_berstein_vazirani',
    category='Algorithms',
    front='Bernstein-Vazirani: how many queries needed?',
    back='1 query quantum vs n queries classical to find hidden bit string s in f(x)=s·x mod 2',
)
