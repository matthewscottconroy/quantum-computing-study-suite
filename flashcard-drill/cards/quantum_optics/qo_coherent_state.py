"""Card: qo_coherent_state"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qo_coherent_state',
    category='Quantum Optics',
    front='Coherent state |α⟩: definition and statistics',
    back='Eigenstate of the annihilation operator: â|α⟩ = α|α⟩.  Photon statistics are Poissonian with ⟨n⟩ = |α|² and Δn = |α|.  Minimal uncertainty state; closest analogue to classical EM field.',
)
