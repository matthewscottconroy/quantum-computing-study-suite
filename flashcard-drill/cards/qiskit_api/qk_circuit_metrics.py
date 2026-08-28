"""Card: qk_circuit_metrics"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qk_circuit_metrics',
    category='Qiskit API',
    front='qc.depth(), qc.size(), qc.count_ops() — what does each return?',
    back="depth(): number of layers on the critical path (H;CX;X on 2 qubits → 3).  size(): total instruction count.  count_ops(): OrderedDict of gate name → count, e.g. {'h': 1, 'cx': 1, 'x': 1}.",
)
