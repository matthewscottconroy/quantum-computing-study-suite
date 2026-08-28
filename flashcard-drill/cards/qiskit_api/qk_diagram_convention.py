"""Card: qk_diagram_convention"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qk_diagram_convention',
    category='Qiskit API',
    front='Circuit diagram conventions: time direction and qubit ordering?',
    back='Time flows LEFT to RIGHT — leftmost gates are applied first (so the diagram order is the reverse of the matrix product).  Qubit q_0 is drawn on the TOP wire, higher indices below; classical wires are at the bottom.',
)
