"""Card: alg_hadamard_test"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='alg_hadamard_test',
    category='Algorithms',
    front='Hadamard test: what does it compute?',
    back='Ancilla |0⟩ → H → controlled-U → H → measure gives P(0) = (1 + Re⟨ψ|U|ψ⟩)/2.  For imaginary part, insert S† on ancilla before final H.',
)
