"""Card: alg_amp_estimation"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='alg_amp_estimation',
    category='Algorithms',
    front='Amplitude estimation vs QPE',
    back='Amplitude estimation uses QPE on a Grover operator to estimate ⟨ψ|A|ψ⟩² with O(1/ε) queries vs O(1/ε²) classically',
)
