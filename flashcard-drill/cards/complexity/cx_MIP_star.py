"""Card: cx_MIP_star"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='cx_MIP_star',
    category='Complexity',
    front='MIP* = RE result (Ji et al. 2020)',
    back='Multi-prover interactive proofs with entangled provers (MIP*) can decide RE-complete problems — shockingly more powerful than MIP = NEXP.  Resolves Connes embedding conjecture.',
)
