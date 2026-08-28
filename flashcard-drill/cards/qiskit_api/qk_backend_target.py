"""Card: qk_backend_target"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qk_backend_target',
    category='Qiskit API',
    front='What is backend.target?',
    back='A Target object: the machine model the transpiler compiles to — supported operation names, qubit count, per-instruction properties (error, duration) and connectivity.  target.operation_names lists the basis gates, e.g. rz/sx/x/cx + measure/reset/delay.',
)
