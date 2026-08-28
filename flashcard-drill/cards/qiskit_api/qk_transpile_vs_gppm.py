"""Card: qk_transpile_vs_gppm"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qk_transpile_vs_gppm',
    category='Qiskit API',
    front='transpile() vs generate_preset_pass_manager() — difference?',
    back='transpile(qc, backend) is a one-shot convenience call.  generate_preset_pass_manager(optimization_level, backend=…) returns a reusable StagedPassManager: pm.run(qc) — preferred when transpiling many circuits with the same settings.  Both default to optimization level 2.',
)
