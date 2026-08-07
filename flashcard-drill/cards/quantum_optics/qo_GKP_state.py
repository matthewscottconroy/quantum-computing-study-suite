"""Card: qo_GKP_state"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qo_GKP_state',
    category='Quantum Optics',
    front='GKP (Gottesman-Kitaev-Preskill) states',
    back='Grid states in phase space that encode a qubit in a harmonic oscillator.  Periodic in both quadratures; shift errors (small x and p displacements) are correctable.  Platform for continuous-variable QEC.',
)
