"""Card: qk_estimator_no_meas"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qk_estimator_no_meas',
    category='Qiskit API',
    front='Can an Estimator circuit contain measurements?',
    back="No — the Estimator computes ⟨ψ|O|ψ⟩ from the (pre-measurement) quantum state; a circuit with measure instructions raises an error ('Cannot apply instruction with classical bits: measure').  Sampler needs measurements; Estimator must NOT have them.",
)
