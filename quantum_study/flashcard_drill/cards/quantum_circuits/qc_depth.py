"""Card: qc_depth"""
from __future__ import annotations
from quantum_study.flashcard_drill.core.models import Flashcard

CARD = Flashcard(
    id='qc_depth',
    category='Quantum Circuits',
    front='Circuit depth: definition',
    back='The length of the longest path from input to output when gates are parallelised.  Determines total run time on hardware.',
)
