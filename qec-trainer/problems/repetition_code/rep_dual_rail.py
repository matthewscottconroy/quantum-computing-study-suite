"""Problem: rep_dual_rail"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='rep_dual_rail',
    category='Repetition Code',
    difficulty='intermediate',
    question='What is dual-rail encoding and what error does it detect?',
    choices=[
        'A qubit encoded as |0̄⟩=|01⟩ and |1̄⟩=|10⟩; it detects photon loss (erasure) errors',
        'Two copies of a qubit in parallel for bit-flip protection',
        'A code using two rails of stabilizers for X and Z separately',
        'A qubit encoded as |0̄⟩=|00⟩ and |1̄⟩=|11⟩; detects phase errors',
    ],
    correct_index=0,
    explanation='Dual-rail encoding represents a qubit as a single photon in one of two modes: |0̄⟩ = |01⟩ (photon in mode 2) and |1̄⟩ = |10⟩ (photon in mode 1). A photon loss event maps |01⟩→|00⟩ or |10⟩→|00⟩ — the total photon number drops from 1 to 0, which is detectable. This is an erasure-detecting code: it flags the loss but cannot correct it. It is used in photonic quantum computing.',
    hints=[
        'Think of encoding a qubit into the position of a single photon across two modes.',
    ],
    grade_mode=GradeMode.AUTO,
)
