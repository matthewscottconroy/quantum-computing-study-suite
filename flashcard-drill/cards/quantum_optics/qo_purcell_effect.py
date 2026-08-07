"""Card: qo_purcell_effect"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qo_purcell_effect',
    category='Quantum Optics',
    front='Purcell effect: cavity modification of emission',
    back='A cavity can enhance spontaneous emission rate by the Purcell factor F_P = 3λ³Q/(4π²V) (Q = quality factor, V = mode volume) or suppress it by being off-resonance.  Used to engineer single-photon emitters.',
)
