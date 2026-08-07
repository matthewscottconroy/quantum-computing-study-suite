"""Card: qc_T_count_hardness"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qc_T_count_hardness',
    category='Quantum Circuits',
    front='T-count minimization complexity',
    back='Minimising the T-count of a Clifford+T circuit is NP-hard.  Heuristic algorithms (e.g., T-par, ZX-calculus rewriting) find near-optimal reductions in practice.',
)
