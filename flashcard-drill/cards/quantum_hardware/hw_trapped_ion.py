"""Card: hw_trapped_ion"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='hw_trapped_ion',
    category='Quantum Hardware',
    front='Trapped-ion qubit: encoding and coherence',
    back='Logical states encoded in hyperfine levels of individual ions (e.g., ⁹Be⁺, ⁴⁰Ca⁺).  T1 can exceed minutes; gate fidelities among the highest of any platform.',
)
