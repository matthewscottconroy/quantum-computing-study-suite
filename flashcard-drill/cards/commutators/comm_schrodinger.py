"""Card: comm_schrodinger"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='comm_schrodinger',
    category='Commutators',
    front='Von Neumann equation: ∂ρ/∂t = ?',
    back="∂ρ/∂t = -i[H, ρ]/ℏ   — the quantum analogue of Liouville's equation for density matrices",
)
