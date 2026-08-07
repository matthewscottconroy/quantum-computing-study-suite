"""Card: qo_g2_function"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qo_g2_function',
    category='Quantum Optics',
    front='Second-order coherence g²(0): formula and values',
    back='g²(0) = ⟨a†a†aa⟩/⟨a†a⟩² = ⟨n(n−1)⟩/⟨n⟩².  Classical light: g²(0) ≥ 1.  Single photon: g²(0) = 0.  Coherent state: g²(0) = 1.  Measurement verifies single-photon sources.',
)
