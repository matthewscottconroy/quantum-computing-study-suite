"""Card: qo_boson_sampling"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qo_boson_sampling',
    category='Quantum Optics',
    front='Boson sampling: why is it hard?',
    back='Sampling from the output distribution of n single photons through a linear interferometer requires computing permanents of complex matrices — #P-hard classically.  Aaronson-Arkhipov 2011.',
)
