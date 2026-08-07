"""Problem: bp_tdesigns"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='bp_tdesigns',
    category='Barren Plateaus',
    difficulty='intermediate',
    question='What is the connection between unitary t-designs and barren plateaus?',
    choices=[
        'Circuits forming approximate t-designs with t≥2 exhibit barren plateaus for global cost functions because their gradient statistics match the Haar-random (uniform) distribution',
        'Only circuits that are exact unitary 1-designs exhibit barren plateaus',
        'Higher t-designs avoid barren plateaus because they provide more structured sampling of the unitary group',
        't-designs are relevant only for quantum error correction, not VQA landscapes',
    ],
    correct_index=0,
    explanation='A unitary t-design reproduces the first t moments of the Haar measure over unitaries. The barren plateau proof (McClean et al. 2018) uses the fact that for circuits forming approximate 2-designs, the second moment of the gradient matches the Haar-random second moment, which is exponentially small. The Clifford group is an exact 3-design; random circuits with O(n log n) depth are approximate 2-designs. This connection means: any circuit deep enough to form an approximate 2-design will exhibit barren plateaus for global costs, regardless of specific gate choices.',
    hints=[
        'A 2-design means gradient second moments match the Haar measure — which gives exponential suppression.',
    ],
    grade_mode=GradeMode.MC,
)
