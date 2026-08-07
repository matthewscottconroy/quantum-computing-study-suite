"""Card: qi_ent_irreversibility"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qi_ent_irreversibility',
    category='Quantum Info',
    front='Entanglement cost vs distillable entanglement',
    back='E_D(ρ) ≤ E_C(ρ) in general for mixed states — unlike pure states where E_D = E_C = S(ρ_A).  The gap is evidence of bound entanglement.',
)
