"""Card: qk_opt_levels"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qk_opt_levels',
    category='Qiskit API',
    front='Transpiler optimization levels 0–3 — what does each mean?',
    back='0: no optimization (just mapping to the target); 1: light optimization; 2: heavy optimization (the DEFAULT); 3: even heavier (best circuits, longest compile time).  Higher levels cost more compile time for shallower circuits.',
)
