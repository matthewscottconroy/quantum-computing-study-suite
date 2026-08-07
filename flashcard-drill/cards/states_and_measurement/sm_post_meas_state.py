"""Card: sm_post_meas_state"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='sm_post_meas_state',
    category='States & Measurement',
    front='Post-measurement state for POVM element Mᵢ',
    back='State after outcome i: σᵢ = √Mᵢ |ψ⟩⟨ψ| √Mᵢ / pᵢ where pᵢ = ⟨ψ|Mᵢ|ψ⟩.  For projectors Mᵢ = Πᵢ this reduces to standard projection.',
)
