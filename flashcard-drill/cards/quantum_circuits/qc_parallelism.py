"""Card: qc_parallelism"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qc_parallelism',
    category='Quantum Circuits',
    front='Quantum parallelism via superposition',
    back='Applying U to |+⟩^n evaluates U on all 2ⁿ inputs simultaneously; but measurement only yields one outcome — useful only when interference extracts global properties',
)
