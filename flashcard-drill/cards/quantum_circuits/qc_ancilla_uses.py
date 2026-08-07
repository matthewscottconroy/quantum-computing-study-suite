"""Card: qc_ancilla_uses"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qc_ancilla_uses',
    category='Quantum Circuits',
    front='Uses of ancilla qubits',
    back='1) Workspace for reversible arithmetic.  2) POVM implementation via Naimark dilation.  3) Syndrome extraction in QEC.  4) Magic state injection for T gates.',
)
