"""Card: cx_NISQ"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='cx_NISQ',
    category='Complexity',
    front='What is the NISQ computational model?',
    back='Noisy Intermediate-Scale Quantum: 50-1000 qubits, no error correction, limited coherence.  Cannot run fault-tolerant algorithms but may show near-term advantage.',
)
