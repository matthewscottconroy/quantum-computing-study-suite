"""Card: ec_hamming_bound"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='ec_hamming_bound',
    category='Error Correction',
    front='Quantum Hamming (Singleton-style) bound',
    back='For an [[n,k,d]] code: n−k ≥ 2(d−1).  The quantum Hamming bound: Σᵢ₌₀^t C(n,i)·3ⁱ ≤ 2^{n−k} where t=⌊(d−1)/2⌋.',
)
