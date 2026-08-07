"""Card: qc_CNOT_resource"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qc_CNOT_resource',
    category='Quantum Circuits',
    front='CNOT count as entanglement resource',
    back='CNOT gates create entanglement; 3 CNOTs are both necessary and sufficient for SWAP.  Minimising CNOT count is key for near-term circuits.',
)
