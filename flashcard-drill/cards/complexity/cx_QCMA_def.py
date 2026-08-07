"""Card: cx_QCMA_def"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='cx_QCMA_def',
    category='Complexity',
    front='What is QCMA?',
    back='Quantum Classical Merlin-Arthur: quantum verifier but classical (bit-string) proof.  QCMA ⊆ QMA; believed strictly weaker since quantum proofs seem more powerful.',
)
