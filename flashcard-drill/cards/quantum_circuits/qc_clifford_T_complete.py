"""Card: qc_clifford_T_complete"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qc_clifford_T_complete',
    category='Quantum Circuits',
    front='Clifford+T completeness: sketch',
    back='H and CNOT generate all Cliffords; T adds a non-Clifford rotation.  Together they generate a dense subgroup of SU(2ⁿ), enabling ε-approximation of any unitary (Solovay-Kitaev).',
)
