"""Card: mbp_OTOC"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='mbp_OTOC',
    category='Many-Body Physics',
    front='Out-of-time-order correlator (OTOC) and scrambling',
    back='F(t) = ⟨W†(t)V†W(t)V⟩ measures how W(t) and V fail to commute.  OTOC decay signals quantum information scrambling — propagation across all degrees of freedom; early-time growth given by Lyapunov exponent.',
)
