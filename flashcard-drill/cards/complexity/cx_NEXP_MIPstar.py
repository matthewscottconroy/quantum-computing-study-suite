"""Card: cx_NEXP_MIPstar"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='cx_NEXP_MIPstar',
    category='Complexity',
    front='NEXP ⊆ MIP* significance',
    back='Entangled provers can verify NEXP problems using only polynomial communication.  Combined with MIP* = RE, this shows entanglement gives unbounded power in multi-prover proofs.',
)
