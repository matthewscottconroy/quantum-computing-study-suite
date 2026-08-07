"""Card: sm_W_state_robustness"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='sm_W_state_robustness',
    category='States & Measurement',
    front='W state vs GHZ state: robustness',
    back='|W⟩ = (|100⟩+|010⟩+|001⟩)/√3 — losing one qubit leaves the remaining two entangled.  |GHZ⟩ loses all entanglement under the same loss.',
)
