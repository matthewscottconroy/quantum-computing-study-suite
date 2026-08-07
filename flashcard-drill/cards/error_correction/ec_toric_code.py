"""Card: ec_toric_code"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='ec_toric_code',
    category='Error Correction',
    front='Toric code: parameters and properties',
    back='[[2n², 2, n]] code on an n×n torus.  Vertex operators (X-type) and plaquette operators (Z-type).  Topological degeneracy 4; anyonic excitations are bosons and fermions.',
)
