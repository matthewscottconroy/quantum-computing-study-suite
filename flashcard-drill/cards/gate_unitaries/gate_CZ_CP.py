"""Card: gate_CZ_CP"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='gate_CZ_CP',
    category='Gate Unitaries',
    front='CZ as a controlled-phase gate',
    back='CZ = CP(π): applies a phase of e^{iπ} = −1 to the |11⟩ component.  CZ is symmetric — either qubit can be considered the control.',
)
