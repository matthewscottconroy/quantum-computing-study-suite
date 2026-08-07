"""Card: qi_distillable_ent"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qi_distillable_ent',
    category='Quantum Info',
    front='Distillable entanglement E_D(ρ)',
    back='Maximum ebits extractable from ρ by LOCC.  E_D ≤ E_C — entanglement manipulation is irreversible for mixed states.',
)
