"""Card: thm_CPTP"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='thm_CPTP',
    category='Theorems',
    front='CPTP map (quantum channel) definition',
    back='Completely Positive Trace-Preserving map: ε(ρ) = Σᵢ KᵢρKᵢ† with ΣᵢKᵢ†Kᵢ = I  (Kraus representation)',
)
