"""Card: qk_execution_modes"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qk_execution_modes',
    category='Qiskit API',
    front='IBM Runtime execution modes: job, session, batch — when is each used?',
    back='Job mode: a single standalone primitive request.  Session: a dedicated window where your jobs get priority scheduling back-to-back — best for iterative/variational loops.  Batch: submit many independent jobs together to minimise queuing overhead — best for parallel workloads.',
)
