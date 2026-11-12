"""Problem: qaoa_structure"""
from __future__ import annotations
from quantum_study.vqa_trainer.core.models import Problem, GradeMode

PROBLEM = Problem(
    id='qaoa_structure',
    category='QAOA',
    difficulty='beginner',
    question='In a depth-p QAOA circuit, which two unitaries are alternated?',
    choices=[
        'U_C(γ) = e^{-iγC} and U_B(β) = e^{-iβB}',
        'Hadamard layer and CNOT layer',
        'Rx(γ) and Rz(β) on each qubit independently',
        'QFT and its inverse',
    ],
    correct_index=0,
    explanation='In full: Problem unitary U_C(γ) = e^{-iγC}  and  Mixer unitary U_B(β) = e^{-iβB}. QAOA applies p rounds of (U_C(γⱼ), U_B(βⱼ)). U_C encodes the cost function C into phases. U_B (typically ⊗Rₓ(2βⱼ)) mixes amplitudes. Parameters {γ, β} are optimised classically.',
    hints=[
        'One operator encodes the problem; the other explores the space.',
    ],
    grade_mode=GradeMode.MC,
)
