"""Card: qi_tsirelson"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qi_tsirelson',
    category='Quantum Info',
    front='Tsirelson bound for CHSH inequality',
    back='CHSH ≤ 2 for local hidden variable models; quantum mechanics allows CHSH ≤ 2√2 ≈ 2.828 — the Tsirelson bound.  Achieved by measuring Bell state in tilted bases.',
)
