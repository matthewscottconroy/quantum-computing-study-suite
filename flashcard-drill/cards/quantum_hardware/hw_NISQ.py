"""Card: hw_NISQ"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='hw_NISQ',
    category='Quantum Hardware',
    front='NISQ definition',
    back='Noisy Intermediate-Scale Quantum: 50–1000 qubits, no error correction, 2-qubit fidelity ~99%.  Coined by Preskill 2018; represents the current generation of quantum hardware.',
)
