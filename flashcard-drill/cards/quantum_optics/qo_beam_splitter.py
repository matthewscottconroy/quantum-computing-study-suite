"""Card: qo_beam_splitter"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qo_beam_splitter',
    category='Quantum Optics',
    front='Beam splitter transformation',
    back='(a, b) → (ta + rb, −ra + tb) where |t|²+|r|²=1.  Unitary; 50:50 BS has t=r=1/√2.  In quantum optics, BS creates entanglement between modes when input is a Fock state.',
)
