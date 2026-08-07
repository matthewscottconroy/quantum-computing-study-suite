"""Card: qc_feynman_kitaev"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qc_feynman_kitaev',
    category='Quantum Circuits',
    front='Feynman-Kitaev circuit-to-Hamiltonian construction',
    back='Maps a T-gate quantum circuit to a k-local Hamiltonian whose ground state is the history state Σₜ|t⟩⊗Uₜ···U₁|ψ⟩/√T.  Basis of QMA-hardness proofs for local Hamiltonians.',
)
