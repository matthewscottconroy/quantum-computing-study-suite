"""Card: qo_fock_state"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qo_fock_state',
    category='Quantum Optics',
    front='Fock state |n⟩: creation and statistics',
    back='|n⟩ = (a†)ⁿ|0⟩/√n! — definite photon number.  ΔN = 0 but phase completely undefined (Δφ → ∞).  Non-classical light; produced by single-photon sources and parametric processes.',
)
