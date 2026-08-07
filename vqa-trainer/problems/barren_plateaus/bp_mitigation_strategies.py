"""Problem: bp_mitigation_strategies"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='bp_mitigation_strategies',
    category='Barren Plateaus',
    difficulty='advanced',
    question='List and briefly explain (3–5 sentences total) two strategies to mitigate barren plateaus in variational quantum algorithms.',
    choices=[],
    correct_index=-1,
    explanation='1. Layer-wise training: train one layer at a time, keeping others fixed. The effective ansatz depth is small during each step, avoiding exponential gradient decay. 2. Identity block initialisation: initialise parameters so each block starts near the identity. This ensures gradients are O(1) at the start regardless of circuit depth. Other strategies: problem-inspired ansätze (fewer irrelevant parameters), local cost functions, quantum natural gradient (better geometry-aware steps).',
    hints=[
        'Think about initialisation strategies and how to reduce effective depth.',
    ],
    grade_mode=GradeMode.CLAUDE,
)
