"""Card: qi_coherence_resource"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qi_coherence_resource',
    category='Quantum Info',
    front='Relative entropy of coherence C(ρ)',
    back='C(ρ) = S(ρ_diag) − S(ρ) where ρ_diag zeroes off-diagonal elements.  Measures coherence relative to a fixed basis; equals 0 for incoherent states.',
)
