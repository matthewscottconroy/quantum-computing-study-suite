"""Card: qo_jaynes_cummings"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qo_jaynes_cummings',
    category='Quantum Optics',
    front='Jaynes-Cummings model Hamiltonian',
    back='H = ωc a†a + ωa σz/2 + g(a†σ₋ + aσ₊) — cavity mode + two-level atom + dipole coupling.  Gives vacuum Rabi splitting 2g; solvable exactly.',
)
