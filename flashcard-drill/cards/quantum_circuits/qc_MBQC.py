"""Card: qc_MBQC"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qc_MBQC',
    category='Quantum Circuits',
    front='Measurement-based quantum computation (MBQC)',
    back='Prepare a cluster state, then drive computation by adaptive single-qubit measurements.  Gate teleportation consumes resource qubits; measurement angle encodes the gate.',
)
