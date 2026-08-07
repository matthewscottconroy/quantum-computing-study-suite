"""Card: thm_no_hiding"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='thm_no_hiding',
    category='Theorems',
    front='No-hiding theorem',
    back='Quantum information that disappears from a system (e.g., bleached by randomization) must appear entirely in the environment — it cannot hide in system-environment correlations.',
)
