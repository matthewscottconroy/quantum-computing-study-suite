"""Card: comm_angular_mom"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='comm_angular_mom',
    category='Commutators',
    front='[Lx, Ly] = ? (angular momentum)',
    back='[Lx, Ly] = iℏLz — cyclic: [Ly,Lz]=iℏLx, [Lz,Lx]=iℏLy.  Same algebra as Pauli matrices (with factor ℏ/2).',
)
