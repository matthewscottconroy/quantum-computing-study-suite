"""Card: qc_distributed_qc"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qc_distributed_qc',
    category='Quantum Circuits',
    front='Distributed quantum computing',
    back='Non-local gates between distant QPUs are implemented via entanglement: teleport one qubit, apply local gate, unteleport.  Shared Bell pairs are the communication resource.',
)
