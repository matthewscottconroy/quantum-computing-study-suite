"""Problem: ft_threshold_necessity"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ft_threshold_necessity',
    category='Fault Tolerance',
    difficulty='advanced',
    question='Explain why fault-tolerant quantum computation requires the threshold theorem, not just quantum error correction alone.',
    choices=[],
    correct_index=-1,
    explanation='Quantum error correction alone removes errors from a code block, but error correction circuits themselves introduce new errors. Without a threshold, adding more error correction could introduce errors faster than it removes them. The threshold theorem guarantees that if the physical error rate p is below a critical value p_th, then each level of concatenated error correction reduces the logical error rate, so adding more levels always helps. Below threshold, the effective error rate decreases doubly-exponentially with concatenation level, enabling arbitrarily long computation. Above threshold, more error correction makes things worse. Error correction without the threshold condition provides no guarantee of long-term computational reliability.',
    hints=[
        'Ask: what happens to the error rate when we add an error correction layer that itself has errors?',
    ],
    grade_mode=GradeMode.CLAUDE,
)
