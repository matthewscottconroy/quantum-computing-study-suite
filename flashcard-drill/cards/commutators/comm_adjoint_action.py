"""Card: comm_adjoint_action"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='comm_adjoint_action',
    category='Commutators',
    front='Adjoint action adₐ definition',
    back='adₐ(B) = [A, B].  Used in Lie algebra theory; repeated application gives the Baker-Hausdorff expansion: e^A B e^{-A} = Σₙ (adₐ)ⁿ(B)/n!',
)
