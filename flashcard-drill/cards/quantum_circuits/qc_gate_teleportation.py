"""Card: qc_gate_teleportation"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qc_gate_teleportation',
    category='Quantum Circuits',
    front='Teleportation-based gate implementation',
    back='Resource state |G⟩ can be consumed to teleport a gate G into the computation.  e.g., consuming |T⟩ applies T to a logical qubit — used in fault-tolerant magic state injection.',
)
