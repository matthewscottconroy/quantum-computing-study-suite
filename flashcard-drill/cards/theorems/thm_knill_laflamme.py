"""Card: thm_knill_laflamme"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='thm_knill_laflamme',
    category='Theorems',
    front='Knill-Laflamme QEC conditions',
    back='Code with projector Π corrects error set {Eₐ} iff ΠEₐ†EᵦΠ = cₐᵦΠ for all a,b — errors must be distinguishable and non-deforming',
)
