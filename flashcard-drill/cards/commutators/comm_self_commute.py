"""Card: comm_self_commute"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='comm_self_commute',
    category='Commutators',
    front='[H, f(H)] = ? for any function f',
    back='[H, f(H)] = 0 — any operator commutes with any function of itself, since they share an eigenbasis.',
)
