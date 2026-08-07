"""Card: alg_var_quantum_sim"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='alg_var_quantum_sim',
    category='Algorithms',
    front='Variational quantum simulation (McLachlan principle)',
    back='Approximate time evolution by minimizing ‖(d/dt − iH)|ψ(θ)⟩‖² over parameter velocities θ̇.  Near-term alternative to Trotterization, but accumulates errors.',
)
