"""Card: cx_circuit_vs_gate_complexity"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='cx_circuit_vs_gate_complexity',
    category='Complexity',
    front='Circuit complexity vs gate complexity',
    back='Gate complexity: total number of gates.  Circuit complexity: depth (parallel time).  A circuit can have high gate complexity but low depth using parallelism, or vice versa.',
)
