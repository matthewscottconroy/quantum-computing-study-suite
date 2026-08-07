"""Problem: ansatz_hardware_efficient"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ansatz_hardware_efficient',
    category='Ansatz Design',
    difficulty='beginner',
    question='A hardware-efficient ansatz is designed to:',
    choices=[
        'Match native gate set and connectivity of the target device',
        'Minimise the number of parameters',
        'Exactly reproduce UCCSD',
        'Use only Clifford gates',
    ],
    correct_index=0,
    explanation="Hardware-efficient ansätze use the device's native gates (e.g. CNOT + Rz) and respect qubit connectivity. They are shallow but may lack physical motivation, risking expressibility–trainability trade-offs.",
    hints=[
        'The goal is fewer SWAP gates and shorter depth on real devices.',
    ],
    grade_mode=GradeMode.MC,
)
