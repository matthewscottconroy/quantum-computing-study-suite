"""Card: comm_uncertainty"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='comm_uncertainty',
    category='Commutators',
    front='Heisenberg uncertainty principle from commutator',
    back='ΔA·ΔB ≥ |⟨[A,B]⟩|/2 — the Robertson uncertainty relation.  For x̂ and p̂: ΔxΔp ≥ ℏ/2 since [x̂,p̂]=iℏ.',
)
