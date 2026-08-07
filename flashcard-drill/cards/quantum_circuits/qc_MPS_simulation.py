"""Card: qc_MPS_simulation"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qc_MPS_simulation',
    category='Quantum Circuits',
    front='MPS simulation of circuits',
    back='A circuit state with Schmidt rank χ across any bipartition can be stored as an MPS with bond dimension χ.  Gates update MPS in O(χ³) time; χ grows exponentially for high-entanglement circuits.',
)
