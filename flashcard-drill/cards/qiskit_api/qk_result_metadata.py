"""Card: qk_result_metadata"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qk_result_metadata',
    category='Qiskit API',
    front='Where do shots and metadata live in a V2 primitive result?',
    back="Per-PUB: result[0].metadata (e.g. {'shots': 1024, …} plus execution info) and result[0].data.<creg>.num_shots.  The PrimitiveResult itself also has result.metadata for job-level information.",
)
