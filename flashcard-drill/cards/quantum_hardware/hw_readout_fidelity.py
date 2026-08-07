"""Card: hw_readout_fidelity"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='hw_readout_fidelity',
    category='Quantum Hardware',
    front='Readout fidelity for common platforms',
    back='Dispersive readout (superconducting): ~99–99.5%.  Fluorescence readout (trapped-ion): ~99.9%.  Photon detection (photonic): ~95%.  Readout errors are often among the largest error sources.',
)
