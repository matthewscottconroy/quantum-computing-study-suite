"""Card: thm_de_finetti_qkd"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='thm_de_finetti_qkd',
    category='Theorems',
    front='Quantum de Finetti theorem application to QKD',
    back='An exchangeable n-qubit state (symmetric under permutations) is close to a mixture of product states.  Enables reduction of QKD security proofs from coherent to i.i.d. attacks.',
)
