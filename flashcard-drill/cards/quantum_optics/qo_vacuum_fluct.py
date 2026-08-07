"""Card: qo_vacuum_fluct"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qo_vacuum_fluct',
    category='Quantum Optics',
    front='Vacuum fluctuations: zero-point uncertainty',
    back='⟨0|x̂²|0⟩ = ℏ/(2mω) — the vacuum has nonzero energy ℏω/2 and fluctuates.  Responsible for spontaneous emission, Casimir effect, and shot noise floor.',
)
