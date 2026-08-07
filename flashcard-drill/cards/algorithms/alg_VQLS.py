"""Card: alg_VQLS"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='alg_VQLS',
    category='Algorithms',
    front='Variational quantum linear solver (VQLS)',
    back='VQA alternative to HHL: minimize ‖A|x⟩−|b⟩‖ over a parameterized ansatz.  Avoids HHL state-preparation requirements but has no proven speedup and faces barren plateaus.',
)
