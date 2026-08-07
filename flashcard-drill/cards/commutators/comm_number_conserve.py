"""Card: comm_number_conserve"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='comm_number_conserve',
    category='Commutators',
    front='When does [H, N] = 0?',
    back='When H conserves particle number, e.g. tunneling hopping terms a†ᵢaⱼ + h.c.  [H,N]=0 means superselection of particle number — no coherent superposition of different photon numbers in a closed system.',
)
