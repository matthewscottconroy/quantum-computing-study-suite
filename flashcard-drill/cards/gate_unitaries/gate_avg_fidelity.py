"""Card: gate_avg_fidelity"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='gate_avg_fidelity',
    category='Gate Unitaries',
    front='Average gate fidelity formula',
    back='F_avg = (d·F_process + 1)/(d + 1)  where F_process = |Tr(U†V)|²/d² and d = 2ⁿ.  Averages over Haar-random input states.',
)
