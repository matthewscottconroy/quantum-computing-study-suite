"""Card: alg_shor_steps"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='alg_shor_steps',
    category='Algorithms',
    front="Shor's algorithm: key steps",
    back='1) Choose random a < N. 2) Check gcd(a,N); if >1, done. 3) Quantum period finding: find r s.t. aʳ ≡ 1 (mod N). 4) Compute gcd(a^{r/2}±1, N).',
)
