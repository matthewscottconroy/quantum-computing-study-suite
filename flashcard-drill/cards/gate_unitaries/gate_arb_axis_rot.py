"""Card: gate_arb_axis_rot"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='gate_arb_axis_rot',
    category='Gate Unitaries',
    front='Rotation about arbitrary axis n̂',
    back='U(θ, n̂) = cos(θ/2)I − i·sin(θ/2)(n̂·σ⃗)  where n̂=(nx,ny,nz) is a unit vector and σ⃗=(X,Y,Z).  Reduces to Rx/Ry/Rz for standard axes.',
)
