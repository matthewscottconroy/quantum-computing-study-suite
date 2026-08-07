"""Card: qc_compile_vs_trans"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qc_compile_vs_trans',
    category='Quantum Circuits',
    front='Compilation vs transpilation in quantum computing',
    back='Compilation: abstract circuit → gate set + optimisation.  Transpilation: additionally maps to hardware topology (connectivity constraints) and optimises for native gates.',
)
