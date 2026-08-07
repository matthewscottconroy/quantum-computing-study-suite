"""Card: mbp_trotter_error"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='mbp_trotter_error',
    category='Many-Body Physics',
    front='Trotterization error in quantum simulation',
    back='First-order: ‖e^{(A+B)t} − e^{At}e^{Bt}‖ ≤ ½t²‖[A,B]‖.  Second-order (symmetric): O(t³).  Commutator norm controls error; small for slowly-varying or commuting Hamiltonians.',
)
