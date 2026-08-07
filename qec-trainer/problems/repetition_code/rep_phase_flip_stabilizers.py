"""Problem: rep_phase_flip_stabilizers"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='rep_phase_flip_stabilizers',
    category='Repetition Code',
    difficulty='beginner',
    question='The 3-qubit phase-flip code encodes |0⟩ → |+++⟩ and |1⟩ → |−−−⟩. Which stabilizer generators does it use?',
    choices=[
        'X₁X₂ and X₂X₃',
        'Z₁Z₂ and Z₂Z₃',
        'X₁Z₂ and Z₂X₃',
        'Z₁X₂ and X₂Z₃',
    ],
    correct_index=0,
    explanation='The phase-flip code is the Hadamard-conjugate of the bit-flip code. Its stabilizers are X₁X₂ and X₂X₃ (products of Pauli X on neighboring qubits). A Z error on qubit i anticommutes with the X stabilizers involving that qubit, yielding a non-trivial syndrome.',
    hints=[
        'Apply H to each qubit of the bit-flip code: Z stabilizers become X stabilizers.',
    ],
    grade_mode=GradeMode.AUTO,
)
