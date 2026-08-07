"""Card: mbp_bravyi_kitaev"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='mbp_bravyi_kitaev',
    category='Many-Body Physics',
    front='Bravyi-Kitaev (BK) transformation',
    back='Encodes fermionic operators with O(log n)-weight Pauli strings (vs O(n) for Jordan-Wigner).  Reduces circuit depth for quantum chemistry simulations on near-term devices.',
)
