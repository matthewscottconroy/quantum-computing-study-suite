"""Card: qc_CZ_CNOT_identity"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qc_CZ_CNOT_identity',
    category='Quantum Circuits',
    front='CZ and CNOT circuit identities',
    back='CZ = (I⊗H)·CNOT·(I⊗H)  and  CNOT = (H⊗H)·CZ·(H⊗H) — CZ is symmetric while CNOT has a directional control/target structure.',
)
