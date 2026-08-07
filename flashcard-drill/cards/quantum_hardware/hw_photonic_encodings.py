"""Card: hw_photonic_encodings"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='hw_photonic_encodings',
    category='Quantum Hardware',
    front='Photonic qubit encodings',
    back='Path encoding (two waveguides), polarization (H/V), time-bin (early/late pulse), and dual-rail (one photon in two modes).  Dual-rail is most common in linear-optics quantum computing proposals.',
)
