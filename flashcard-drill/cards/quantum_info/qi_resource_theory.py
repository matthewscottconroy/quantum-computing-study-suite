"""Card: qi_resource_theory"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qi_resource_theory',
    category='Quantum Info',
    front='Resource theory framework',
    back='Specifies free states (no resource), free operations (cannot create resource), and resource measures.  Examples: entanglement (LOCC free), coherence (dephasing free), thermodynamics (Gibbs states free).',
)
