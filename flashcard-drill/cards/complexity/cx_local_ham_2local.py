"""Card: cx_local_ham_2local"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='cx_local_ham_2local',
    category='Complexity',
    front='Why is 2-local Hamiltonian QMA-complete?',
    back="Kitaev's circuit-to-Hamiltonian construction encodes a QMA verification circuit as a 5-local Hamiltonian; later simplified to 2-local.  Ground state encodes the history of the computation.",
)
