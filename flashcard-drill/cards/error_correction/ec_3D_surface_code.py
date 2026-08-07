"""Card: ec_3D_surface_code"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='ec_3D_surface_code',
    category='Error Correction',
    front='3D surface codes and transversal T',
    back='3D surface codes can implement a transversal T gate, unlike 2D codes.  Proposed for fault-tolerant architectures where the extra spatial dimension provides the missing Clifford+T universality.',
)
