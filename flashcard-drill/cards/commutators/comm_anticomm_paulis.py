"""Card: comm_anticomm_paulis"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='comm_anticomm_paulis',
    category='Commutators',
    front='Anticommutator {X,Z}, {X,Y}, {Y,Z} = ?',
    back='{X,Z} = {X,Y} = {Y,Z} = 0 — all pairs of distinct Pauli matrices anticommute.  Only {P,P} = 2I for P∈{X,Y,Z}.',
)
