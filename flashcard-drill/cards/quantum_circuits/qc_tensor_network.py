"""Card: qc_tensor_network"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qc_tensor_network',
    category='Quantum Circuits',
    front='Tensor network contraction for circuit simulation',
    back='Circuit simulation maps to a 3D tensor network.  Contraction order determines cost; optimal contraction is NP-hard but heuristic methods (e.g., cotengra) handle large shallow circuits.',
)
