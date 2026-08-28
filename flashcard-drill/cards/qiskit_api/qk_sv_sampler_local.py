"""Card: qk_sv_sampler_local"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qk_sv_sampler_local',
    category='Qiskit API',
    front='How do you run the Sampler primitive locally without hardware?',
    back='from qiskit.primitives import StatevectorSampler; sampler = StatevectorSampler(seed=42); job = sampler.run([qc], shots=1024).  Ships with qiskit itself — ideal (noiseless) sampling with the same V2 PUB/result interface as the runtime version.',
)
