"""Card: mbp_jordan_wigner"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='mbp_jordan_wigner',
    category='Many-Body Physics',
    front='Jordan-Wigner transformation',
    back='Maps fermionic operators to qubit operators: cⱼ = (Π_{k<j} Zₖ) ⊗ (X+iY)ⱼ/2.  Z-string preserves fermionic anticommutation.  Gives O(n)-weight Pauli strings in 1D.',
)
