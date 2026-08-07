"""Card: alg_phase_kickback"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='alg_phase_kickback',
    category='Algorithms',
    front='Phase kickback mechanism',
    back='If U|u⟩=e^{iφ}|u⟩, then control-U acting on |+⟩|u⟩ → e^{iφ/2}(|0⟩+e^{iφ}|1⟩)⊗|u⟩/√2 — phase transferred to control qubit',
)
