"""Card: thm_Solovay_Kitaev"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='thm_Solovay_Kitaev',
    category='Theorems',
    front='Solovay-Kitaev theorem',
    back='Any single-qubit gate can be approximated to ε using O(log^c(1/ε)) gates from a universal finite gate set (c≈3.97)',
)
