"""Card: comm_lindblad_H"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='comm_lindblad_H',
    category='Commutators',
    front='[H, ρ] term in the Lindblad equation',
    back='The −i[H,ρ] term drives coherent Hamiltonian evolution.  The Lindblad dissipators L_k ρ L_k† − ½{L_k†L_k, ρ} add decoherence.',
)
