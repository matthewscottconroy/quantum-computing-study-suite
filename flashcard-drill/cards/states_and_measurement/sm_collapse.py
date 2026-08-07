"""Card: sm_collapse"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='sm_collapse',
    category='States & Measurement',
    front='State after projective measurement yielding outcome a?',
    back='Post-measurement state = Πₐ|ψ⟩ / ‖Πₐ|ψ⟩‖  where Πₐ = |a⟩⟨a|.  For density matrices: Πₐρ Πₐ / Tr(Πₐρ)',
)
