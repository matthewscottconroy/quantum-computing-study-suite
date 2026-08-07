"""Card: hw_sc_qubit_types"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='hw_sc_qubit_types',
    category='Quantum Hardware',
    front='What are the main superconducting qubit types?',
    back='Transmon, fluxonium, and charge qubit.  Transmon is most common: large Josephson junction shunted by a capacitor for reduced charge noise.',
)
