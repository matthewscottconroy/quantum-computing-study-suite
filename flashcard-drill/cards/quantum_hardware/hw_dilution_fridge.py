"""Card: hw_dilution_fridge"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='hw_dilution_fridge',
    category='Quantum Hardware',
    front='Why do superconducting qubits need dilution refrigerators?',
    back='Superconducting qubits operate at ~15 mK to suppress thermal photon occupation (kT ≪ ℏω_q) and maintain superconductivity.  Dilution refrigerators achieve this via He-3/He-4 mixing.',
)
