"""Problem: rep_5qubit_stabilizers"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='rep_5qubit_stabilizers',
    category='Repetition Code',
    difficulty='advanced',
    question='What are the four stabilizer generators of the [[5,1,3]] perfect code?',
    choices=[
        'XZZXI, IXZZX, XIXZZ, ZXIXZ',
        'ZZZZZ, XXXXX, ZZIII, IIZZZ',
        'XZXZX, ZXZXZ, XXXXX, ZZZZZ',
        'XZZXI, IXZZX, ZXIXZ, ZZXIX',
    ],
    correct_index=0,
    explanation='The [[5,1,3]] code has generators: g₁=XZZXI, g₂=IXZZX, g₃=XIXZZ, g₄=ZXIXZ. These are cyclic permutations of XZZXI. They form 4 independent generators for a code on 5 qubits encoding 1 logical qubit (5−4=1). Each generator has weight 4, and the code corrects any single-qubit error.',
    hints=[
        'The generators of the 5-qubit code are cyclic shifts of a single weight-4 string.',
    ],
    grade_mode=GradeMode.AUTO,
)
