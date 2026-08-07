"""Card: gate_CT"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='gate_CT',
    category='Gate Unitaries',
    front='Controlled-T gate in quantum arithmetic',
    back='CT applies T = diag(1, e^{iπ/4}) to the target when control = |1⟩.  The T-count of CT is 1; it appears in Toffoli decompositions and quantum adders.',
)
