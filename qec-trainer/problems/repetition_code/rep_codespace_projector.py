"""Problem: rep_codespace_projector"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='rep_codespace_projector',
    category='Repetition Code',
    difficulty='intermediate',
    question='The code space of the 3-qubit bit-flip code is:',
    choices=[
        'span{|000⟩, |111⟩} — all states α|000⟩ + β|111⟩',
        'span{|000⟩, |001⟩, |010⟩, |011⟩}',
        'Only the state |000⟩ + |111⟩)/√2',
        'The full 3-qubit Hilbert space',
    ],
    correct_index=0,
    explanation='The code space is the simultaneous +1 eigenspace of both stabilizers Z₁Z₂ and Z₂Z₃. This is spanned by |000⟩ and |111⟩, allowing an arbitrary logical qubit α|000⟩ + β|111⟩ to be encoded. The code space is 2-dimensional inside the 8-dimensional 3-qubit Hilbert space.',
    hints=[
        'Find the states satisfying Z₁Z₂ = +1 AND Z₂Z₃ = +1 simultaneously.',
    ],
    grade_mode=GradeMode.AUTO,
)
