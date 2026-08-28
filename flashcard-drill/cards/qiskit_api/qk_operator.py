"""Card: qk_operator"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qk_operator',
    category='Qiskit API',
    front='What does Operator(qc) give you?',
    back='The full unitary matrix of the circuit as an Operator object (2ⁿ×2ⁿ).  op.data is the ndarray; op.is_unitary() checks unitarity; operators support @/compose/tensor and can be used in sv.evolve(op).',
)
