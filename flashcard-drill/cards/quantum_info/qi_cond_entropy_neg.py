"""Card: qi_cond_entropy_neg"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qi_cond_entropy_neg',
    category='Quantum Info',
    front='Can quantum conditional entropy S(A|B) be negative?',
    back='Yes! S(A|B) = S(AB) − S(B) can be negative for entangled states (e.g., S(A|B) = −1 for a Bell state).  Negative conditional entropy is a signature of entanglement.',
)
