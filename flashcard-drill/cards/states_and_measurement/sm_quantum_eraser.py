"""Card: sm_quantum_eraser"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='sm_quantum_eraser',
    category='States & Measurement',
    front='Quantum eraser experiment',
    back='Which-path information destroys interference.  If the which-path record is erased (before or after detection), interference is restored — demonstrating that information, not physical disturbance, destroys coherence.',
)
