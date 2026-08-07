"""Card: gate_SWAP"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='gate_SWAP',
    category='Gate Unitaries',
    front='SWAP in terms of CNOTs',
    back='SWAP = CNOT_{12} · CNOT_{21} · CNOT_{12}  (3 CNOTs)',
)
