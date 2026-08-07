"""Card: sm_bloch_equator"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='sm_bloch_equator',
    category='States & Measurement',
    front='Bloch sphere: what states lie on the equator?',
    back='±X axis: |±⟩; ±Y axis: |±Y⟩ = (|0⟩±i|1⟩)/√2; all equatorial states are equal superpositions of |0⟩ and |1⟩',
)
