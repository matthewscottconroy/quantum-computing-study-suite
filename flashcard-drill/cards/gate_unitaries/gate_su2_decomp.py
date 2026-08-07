"""Card: gate_su2_decomp"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='gate_su2_decomp',
    category='Gate Unitaries',
    front='Any SU(2) rotation in terms of Rz and Ry?',
    back='U = Rz(α)·Ry(β)·Rz(γ) for some angles α,β,γ — ZYZ Euler decomposition',
)
