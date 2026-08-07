"""Card: ec_amplitude_damping"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='ec_amplitude_damping',
    category='Error Correction',
    front='Amplitude damping channel (T1 decay)',
    back='Kraus: K₀=[[1,0],[0,√(1−γ)]], K₁=[[0,√γ],[0,0]].  Describes energy relaxation |1⟩→|0⟩ with rate γ.  γ = 1−e^{−t/T1}.',
)
