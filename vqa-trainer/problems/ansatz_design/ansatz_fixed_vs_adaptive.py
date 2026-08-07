"""Problem: ansatz_fixed_vs_adaptive"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ansatz_fixed_vs_adaptive',
    category='Ansatz Design',
    difficulty='beginner',
    question='What is the key difference between a fixed-structure ansatz and an adaptive ansatz like ADAPT-VQE?',
    choices=[
        'Fixed ansatz: pre-chosen layer structure; adaptive ansatz: operators added greedily during optimisation',
        'Fixed ansatz: only single-qubit gates; adaptive ansatz: includes entangling gates',
        'Fixed ansatz: hardware-efficient; adaptive ansatz: requires all-to-all connectivity',
        'Fixed ansatz: chemically motivated; adaptive ansatz: uses random gate sequences',
    ],
    correct_index=0,
    explanation='A fixed-structure ansatz (e.g. hardware-efficient or UCCSD) specifies gate types, layer count, and connectivity before optimisation begins. An adaptive ansatz (e.g. ADAPT-VQE, MCCI-QE) builds the circuit dynamically: at each iteration it evaluates which operator from a predefined pool would most reduce the energy (largest gradient), appends it, then re-optimises all parameters. Adaptive ansätze tend to produce more compact circuits but require more classical overhead.',
    hints=[
        'One approach builds the circuit before training; the other grows it during training.',
    ],
    grade_mode=GradeMode.MC,
)
