"""Card: ec_pauli_channel"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='ec_pauli_channel',
    category='Error Correction',
    front='Pauli channel definition',
    back='ε(ρ) = (1−px−py−pz)ρ + pxXρX + pyYρY + pzZρZ.  The depolarising channel is the special case px=py=pz=p/3.',
)
