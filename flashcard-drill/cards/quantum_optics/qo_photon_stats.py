"""Card: qo_photon_stats"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qo_photon_stats',
    category='Quantum Optics',
    front='Photon bunching vs antibunching',
    back='Coherent light: Poissonian (g²(0)=1).  Thermal light: super-Poissonian, bunched (g²(0)=2).  Single-photon source: sub-Poissonian, antibunched (g²(0)=0).  g²(0) distinguishes classical from quantum light.',
)
