"""Card: qo_cat_qubit"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qo_cat_qubit',
    category='Quantum Optics',
    front='Cat qubit as superposition of coherent states',
    back='Logical qubit: |0_L⟩ ∝ |α⟩+|−α⟩, |1_L⟩ ∝ |α⟩−|−α⟩.  Bit-flip errors exponentially suppressed with |α|²; phase-flip errors grow linearly.  Biased noise enables efficient QEC.',
)
