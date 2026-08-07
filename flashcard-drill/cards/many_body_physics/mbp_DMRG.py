"""Card: mbp_DMRG"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='mbp_DMRG',
    category='Many-Body Physics',
    front='DMRG algorithm',
    back='Density Matrix Renormalization Group: variationally optimises an MPS ansatz by sweeping through bonds.  The gold standard classical algorithm for 1D quantum systems; extends to quasi-2D with χ ∝ exp(width).',
)
