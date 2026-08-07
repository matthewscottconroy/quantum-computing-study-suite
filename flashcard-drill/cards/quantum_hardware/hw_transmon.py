"""Card: hw_transmon"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='hw_transmon',
    category='Quantum Hardware',
    front='Why does the transmon qubit have low charge noise?',
    back='Large EJ/EC ratio (EJ = Josephson energy, EC = charging energy) flattens the energy-band dispersion vs gate charge.  Charge noise sensitivity decreases exponentially with EJ/EC at the cost of reduced anharmonicity.',
)
