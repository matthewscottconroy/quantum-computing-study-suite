"""Card: mbp_hubbard"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='mbp_hubbard',
    category='Many-Body Physics',
    front='Hubbard model: Hamiltonian terms',
    back='H = −t Σ⟨i,j⟩,σ (cᵢσ†cⱼσ + h.c.) + U Σᵢ nᵢ↑nᵢ↓.  Hopping t delocalises electrons; on-site repulsion U drives Mott insulator transition.',
)
