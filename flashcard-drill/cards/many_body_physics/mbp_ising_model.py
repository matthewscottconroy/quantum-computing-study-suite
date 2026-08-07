"""Card: mbp_ising_model"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='mbp_ising_model',
    category='Many-Body Physics',
    front='Transverse-field Ising model Hamiltonian',
    back='H = −J Σᵢ ZᵢZᵢ₊₁ − h Σᵢ Xᵢ.  Quantum phase transition at h/J = 1 between ordered (|↑↑…⟩ favored) and disordered (|+⟩^⊗n favored) phases.',
)
