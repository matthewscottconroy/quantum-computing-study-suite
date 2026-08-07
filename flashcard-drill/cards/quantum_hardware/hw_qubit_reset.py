"""Card: hw_qubit_reset"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='hw_qubit_reset',
    category='Quantum Hardware',
    front='Active vs thermalization qubit reset',
    back='Thermalization reset: wait ~5T1 for qubit to relax to |0⟩ — slow.  Active reset: measure, then apply X if result is |1⟩ — ~100× faster; essential for fast error correction cycles.',
)
