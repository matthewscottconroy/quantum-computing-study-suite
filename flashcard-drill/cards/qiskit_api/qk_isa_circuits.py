"""Card: qk_isa_circuits"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qk_isa_circuits',
    category='Qiskit API',
    front='What is an ISA circuit and why do runtime primitives require one?',
    back="An Instruction Set Architecture circuit: already transpiled to the target backend's basis gates and qubit connectivity (its Target).  IBM Runtime primitives (SamplerV2/EstimatorV2) reject non-ISA circuits — you must run transpile/a preset pass manager against the backend first.",
)
