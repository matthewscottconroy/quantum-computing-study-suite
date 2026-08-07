"""Card: qi_monogamy"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qi_monogamy',
    category='Quantum Info',
    front='Monogamy of entanglement',
    back='If A is maximally entangled with B, it cannot be entangled with any third party C.  Quantified by CKW (Coffman-Kundu-Wootters) inequality: τ(A|BC) ≥ τ(AB) + τ(AC).',
)
