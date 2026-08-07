"""Card: comm_anti_herm"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='comm_anti_herm',
    category='Commutators',
    front='If A and B are Hermitian, is [A,B] Hermitian or anti-Hermitian?',
    back='[A,B]† = [B†,A†] = [B,A] = −[A,B], so [A,B] is anti-Hermitian.  Therefore i[A,B] is Hermitian — it is an observable.',
)
