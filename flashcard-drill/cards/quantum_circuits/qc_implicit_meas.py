"""Card: qc_implicit_meas"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qc_implicit_meas',
    category='Quantum Circuits',
    front='Principle of implicit measurement',
    back='Unmeasured output qubits can be replaced by tracing over them — their existence does not affect statistics of the measured subsystem.  Justifies focusing on measured qubits only.',
)
