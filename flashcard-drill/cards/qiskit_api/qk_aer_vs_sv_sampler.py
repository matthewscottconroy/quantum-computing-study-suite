"""Card: qk_aer_vs_sv_sampler"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qk_aer_vs_sv_sampler',
    category='Qiskit API',
    front='AerSimulator vs StatevectorSampler — how do they differ?',
    back='AerSimulator (qiskit-aer): a high-performance backend with backend.run(), many methods (statevector, MPS, stabilizer) and noise-model support.  StatevectorSampler (qiskit.primitives): the built-in ideal reference implementation of the SamplerV2 primitive interface — no noise, no separate install.',
)
