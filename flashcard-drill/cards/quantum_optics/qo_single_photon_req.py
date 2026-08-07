"""Card: qo_single_photon_req"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qo_single_photon_req',
    category='Quantum Optics',
    front='Single-photon source requirements',
    back='High purity (g²(0) ≈ 0), high indistinguishability (photons identical for HOM interference), and high extraction efficiency.  Key metrics for photonic quantum computing and QKD.',
)
