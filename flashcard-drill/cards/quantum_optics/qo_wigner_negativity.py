"""Card: qo_wigner_negativity"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qo_wigner_negativity',
    category='Quantum Optics',
    front='Wigner function negativity as quantum resource',
    back='Negativity of W(x,p) is a necessary (but not sufficient) condition for quantum advantage in continuous-variable computing.  Coherent and squeezed states have non-negative W; Fock states and cat states do not.',
)
