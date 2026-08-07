"""Card: qo_LOCC_photons"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qo_LOCC_photons',
    category='Quantum Optics',
    front='Why does linear optics limit entanglement operations?',
    back='Linear optics implements Gaussian unitaries and LOCC; it cannot deterministically create entanglement between photonic modes without nonlinear elements or measurement-induced nonlinearity (as in KLM).',
)
