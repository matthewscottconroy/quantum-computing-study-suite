"""Card: qo_squeezing_param"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qo_squeezing_param',
    category='Quantum Optics',
    front='Squeezing parameter r: effect on quadrature variances',
    back='Var(X) = e^{-2r}/4, Var(P) = e^{2r}/4.  For r > 0, X is squeezed below vacuum level; product Var(X)·Var(P) = 1/16 (saturates uncertainty relation).',
)
