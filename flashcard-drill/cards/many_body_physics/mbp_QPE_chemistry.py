"""Card: mbp_QPE_chemistry"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='mbp_QPE_chemistry',
    category='Many-Body Physics',
    front='Quantum phase estimation for quantum chemistry',
    back='QPE on a Trotterized or qubitized molecular Hamiltonian estimates ground-state energy to chemical accuracy (~1.6 mHa).  Resource requirements motivate fault-tolerant hardware development.',
)
