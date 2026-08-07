"""Card: alg_HHL_complexity"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='alg_HHL_complexity',
    category='Algorithms',
    front='HHL complexity: gate count',
    back='O(log(N)·κ²·ε⁻¹) where N is matrix dimension, κ is condition number, ε is precision.  Exponential speedup in N, but caveats: requires efficient oracles and quantum readout.',
)
