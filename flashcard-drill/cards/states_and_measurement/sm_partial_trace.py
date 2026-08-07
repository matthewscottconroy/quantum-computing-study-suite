"""Card: sm_partial_trace"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='sm_partial_trace',
    category='States & Measurement',
    front='Partial trace: how to get reduced state ρ_A?',
    back='ρ_A = Tr_B(ρ_AB) = Σⱼ (I_A⊗⟨j|_B) ρ_AB (I_A⊗|j⟩_B)  — trace out subsystem B over any basis {|j⟩}',
)
