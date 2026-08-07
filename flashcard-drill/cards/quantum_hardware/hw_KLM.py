"""Card: hw_KLM"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='hw_KLM',
    category='Quantum Hardware',
    front='KLM scheme: linear optics quantum computation',
    back='Knill-Laflamme-Milburn (2001): universal quantum computing with linear optics, single-photon sources, and photon-number-resolving detectors using postselection.  Resource overhead is large; motivates fusion-based approaches.',
)
