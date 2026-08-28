"""Card: qk_sparsepauliop"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qk_sparsepauliop',
    category='Qiskit API',
    front='How is SparsePauliOp constructed?',
    back="SparsePauliOp('ZZ') for a single Pauli string; SparsePauliOp.from_list([('XX', 0.5), ('ZI', -1.0)]) for weighted sums; or SparsePauliOp(['XX','YY'], coeffs=[1,2]).  It is the standard observable type for the Estimator primitive.",
)
