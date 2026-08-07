"""Card: alg_RSA_resources"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='alg_RSA_resources',
    category='Algorithms',
    front='Resource estimate to break RSA-2048 with Shor',
    back='~4000 logical qubits and ~10⁸ Clifford + ~3×10⁹ T gates (Beauregard-style; varies by implementation).  Requires fault-tolerant hardware far beyond current NISQ devices.',
)
