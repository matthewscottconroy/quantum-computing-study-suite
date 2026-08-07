"""Card: thm_no_communication"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='thm_no_communication',
    category='Theorems',
    front='No-communication theorem',
    back="Local measurements on one half of an entangled state cannot transmit information to the other party.  Marginal statistics on Bob's side are unaffected by Alice's choice of measurement.",
)
