"""Card: ec_phase_damping"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='ec_phase_damping',
    category='Error Correction',
    front='Phase damping channel (T2 dephasing)',
    back='Kraus: K₀=[[1,0],[0,√(1−λ)]], K₁=[[0,0],[0,√λ]].  Destroys off-diagonal coherences without energy exchange.  λ = 1−e^{−t/T₂*}.',
)
