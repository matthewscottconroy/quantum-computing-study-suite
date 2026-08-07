"""Card: qi_ent_swapping"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qi_ent_swapping',
    category='Quantum Info',
    front='Entanglement swapping protocol',
    back='Alice-Bob and Bob-Charlie share Bell pairs.  Bob Bell-measures his two qubits; result: Alice-Charlie are now entangled without ever interacting.  Foundation of quantum repeaters.',
)
