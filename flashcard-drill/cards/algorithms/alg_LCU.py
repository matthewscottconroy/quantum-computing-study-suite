"""Card: alg_LCU"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='alg_LCU',
    category='Algorithms',
    front='Linear combination of unitaries (LCU)',
    back='Implements Σᵢ cᵢUᵢ using PREPARE and SELECT oracles probabilistically.  Key subroutine for Hamiltonian simulation and block encoding constructions.',
)
