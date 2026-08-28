"""Card: qk_estimator_pub"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qk_estimator_pub',
    category='Qiskit API',
    front='What is an Estimator PUB and its shape?',
    back="(circuit, observables, parameter_values, precision) — e.g. estimator.run([(qc, SparsePauliOp('ZZ'))]).  Observables are SparsePauliOp/Pauli-like; parameter_values bind circuit parameters; only circuit + observables are required.",
)
