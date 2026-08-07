"""Card: qo_wigner_func"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qo_wigner_func',
    category='Quantum Optics',
    front='Wigner function: definition',
    back='W(x,p) = (1/πℏ) ∫ ⟨x+y|ρ|x−y⟩ e^{2ipy/ℏ} dy — a quasi-probability distribution over phase space.  Integrates to correct marginals but can be negative.',
)
