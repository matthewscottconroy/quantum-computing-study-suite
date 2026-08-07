"""Card: alg_quantum_counting"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='alg_quantum_counting',
    category='Algorithms',
    front='Quantum counting algorithm',
    back='Run QPE on the Grover iterate G = −H^n(2|0⟩⟨0|−I)H^n · O_x.  QPE yields the eigenphase θ = 2arcsin(√(M/N)) where M is the number of solutions.',
)
