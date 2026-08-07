"""Card: qc_solovay_kitaev"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qc_solovay_kitaev',
    category='Quantum Circuits',
    front='Solovay-Kitaev theorem for circuit compilation',
    back='Any single-qubit gate can be ε-approximated using O(log^c(1/ε)) gates from a universal finite gate set; c ≈ 3.97 originally, improved to ~1 with better constructions',
)
