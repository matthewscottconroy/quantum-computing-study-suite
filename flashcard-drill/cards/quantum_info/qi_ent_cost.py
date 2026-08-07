"""Card: qi_ent_cost"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qi_ent_cost',
    category='Quantum Info',
    front='Entanglement cost E_C(ρ)',
    back='Minimum ebits needed to prepare ρ using LOCC.  E_C(ρ) = lim_{n→∞} E_F(ρ^{⊗n})/n where E_F is entanglement of formation.',
)
