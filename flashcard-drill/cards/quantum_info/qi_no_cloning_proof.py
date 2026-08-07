"""Card: qi_no_cloning_proof"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qi_no_cloning_proof',
    category='Quantum Info',
    front='Sketch: why does no-cloning follow from linearity?',
    back='Assume U|ψ⟩|0⟩=|ψ⟩|ψ⟩.  Apply to |ψ⟩=|0⟩+|1⟩: linearity gives |00⟩+|11⟩ ≠ (|0⟩+|1⟩)⊗²=(|00⟩+|01⟩+|10⟩+|11⟩)/2. Contradiction.',
)
