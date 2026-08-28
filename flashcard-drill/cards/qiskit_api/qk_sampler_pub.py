"""Card: qk_sampler_pub"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qk_sampler_pub',
    category='Qiskit API',
    front='What is a Sampler PUB and its shape?',
    back='A Primitive Unified Bloc: (circuit, parameter_values, shots) — e.g. sampler.run([(qc, [np.pi], 256)]).  A bare circuit is a valid PUB when there are no parameters.  Shots precedence: per-PUB shots > run(shots=…) > default.',
)
