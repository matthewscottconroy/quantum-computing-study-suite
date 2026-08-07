"""Card: sm_weak_value"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='sm_weak_value',
    category='States & Measurement',
    front='Weak value definition',
    back='⟨A⟩_w = ⟨ψ_f|A|ψ_i⟩ / ⟨ψ_f|ψ_i⟩ — the weak value of A between pre-selected state |ψ_i⟩ and post-selected state |ψ_f⟩.  Can lie outside the eigenvalue spectrum of A.',
)
