"""Card: sm_born_rule"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='sm_born_rule',
    category='States & Measurement',
    front='Born rule: P(outcome a) = ?',
    back='P(a) = |⟨a|ψ⟩|²  for projective measurement.  More generally: P(a) = Tr(Πₐ|ψ⟩⟨ψ|) = Tr(Πₐρ)',
)
