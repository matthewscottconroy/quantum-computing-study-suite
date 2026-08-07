"""Card: mbp_scrambling"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='mbp_scrambling',
    category='Many-Body Physics',
    front='Quantum scrambling: definition',
    back='Information initially localized in a few qubits spreads to highly non-local correlations.  Black holes are fast scramblers (scrambling time O(log n)).  Measured by OTOC decay and tripartite mutual information.',
)
